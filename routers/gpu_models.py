"""
GPU-accelerated 3D model generation with TripoSR
Image-to-3D conversion with real-time progress tracking
Communicates with local GPU worker for actual generation
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, Dict
import uuid
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import io
import httpx
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gpu", tags=["GPU 3D Models"])

# In-memory job storage (use database in production)
jobs: Dict[str, Dict] = {}

# Configuration
OUTPUT_DIR = Path("static/models/gpu")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GPU Worker configuration
GPU_WORKER_URL = os.getenv("GPU_WORKER_URL", "http://localhost:8001")
GPU_WORKER_API_KEY = os.getenv("GPU_WORKER_API_KEY", "")

class JobStatus(BaseModel):
    job_id: str
    status: str  # "queued", "processing", "complete", "failed"
    progress: int = Field(ge=0, le=100)
    message: str
    glb_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

async def poll_worker_status(job_id: str, worker_job_id: str):
    """Poll GPU worker for job completion"""
    max_attempts = 150  # 5 minutes with 2-second intervals
    attempt = 0
    
    # Store worker job ID for later use
    jobs[job_id]["worker_job_id"] = worker_job_id
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            while attempt < max_attempts:
                try:
                    # Check worker status
                    response = await client.get(f"{GPU_WORKER_URL}/status/{worker_job_id}")
                    
                    if response.status_code == 200:
                        worker_job = response.json()
                        
                        # Update our job with worker status
                        if worker_job["status"] == "processing":
                            jobs[job_id]["status"] = "processing"
                            jobs[job_id]["progress"] = min(90, 20 + (attempt * 2))  # Estimate progress
                            jobs[job_id]["message"] = "Generating 3D model on GPU worker..."
                        
                        elif worker_job["status"] == "complete":
                            # Don't download - Railway filesystem is ephemeral!
                            # Instead, proxy the GLB through our /gpu/preview endpoint
                            jobs[job_id]["status"] = "complete"
                            jobs[job_id]["progress"] = 100
                            jobs[job_id]["message"] = "Model generated successfully"
                            jobs[job_id]["glb_url"] = f"/gpu/preview/{job_id}.glb"  # Proxy endpoint
                            jobs[job_id]["generation_time"] = worker_job.get("generation_time")
                            jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                            logger.info(f"✅ Job {job_id} completed - GLB available at worker")
                            return
                        
                        elif worker_job["status"] == "failed":
                            raise Exception(worker_job.get("error", "Worker generation failed"))
                    
                    await asyncio.sleep(2)
                    attempt += 1
                    
                except httpx.RequestError as e:
                    logger.warning(f"Worker polling error (attempt {attempt}): {e}")
                    await asyncio.sleep(2)
                    attempt += 1
            
            # Timeout
            raise Exception("Generation timed out after 5 minutes")
            
    except Exception as e:
        logger.error(f"❌ Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = "Generation failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"

async def process_image_to_3d(job_id: str, image_data: bytes, prompt: str, 
                               texture_resolution: int = 2048, mc_resolution: int = 384):
    """
    Send image to GPU worker for processing
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Sending to GPU worker..."
        
        # Save image temporarily
        temp_image_path = OUTPUT_DIR / f"temp_{job_id}.png"
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        
        # Send to GPU worker
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            if GPU_WORKER_API_KEY:
                headers["X-API-Key"] = GPU_WORKER_API_KEY
            
            # Send image file to GPU worker
            logger.info(f"Sending job {job_id} to GPU worker at {GPU_WORKER_URL}")
            
            # Create multipart form data
            files = {
                'image': ('image.png', image_data, 'image/png')
            }
            data = {
                'texture_resolution': texture_resolution,
                'mc_resolution': mc_resolution
            }
            
            response = await client.post(
                f"{GPU_WORKER_URL}/generate-from-image",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Worker rejected request: {response.text}")
            
            worker_response = response.json()
            worker_job_id = worker_response["job_id"]
            
            logger.info(f"GPU worker accepted job {job_id} as worker job {worker_job_id}")
            
            # Clean up temp image
            if temp_image_path.exists():
                temp_image_path.unlink()
            
            # Poll worker for completion
            await poll_worker_status(job_id, worker_job_id)
        
    except Exception as e:
        logger.error(f"❌ Failed to process job {job_id}: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = "Generation failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"

@router.post("/generate", response_model=JobStatus)
async def generate_gpu_model(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="Input image file (PNG, JPG)"),
    texture_resolution: int = Form(2048, description="Texture quality (512, 1024, 2048, 4096)"),
    mc_resolution: int = Form(384, description="Mesh detail (128, 256, 384, 512)")
):
    """
    Generate a 3D model from an image using GPU acceleration
    Returns a job ID for tracking progress
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image (PNG, JPG, etc.)"
            )
        
        # Read image data
        image_data = await image.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Validate image can be opened
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )
        
        # Create job
        job_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Job queued",
            "glb_url": None,
            "created_at": timestamp,
            "completed_at": None,
            "error": None
        }
        
        # Extract prompt from image filename or use default
        prompt = f"3D model from uploaded image"
        
        # Start processing in background
        background_tasks.add_task(process_image_to_3d, job_id, image_data, prompt, 
                                 texture_resolution, mc_resolution)
        
        logger.info(f"Created GPU generation job: {job_id} (texture:{texture_resolution}, mc:{mc_resolution})")
        
        return JobStatus(**jobs[job_id])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating GPU generation job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@router.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a GPU generation job - frontend polls this every 2 seconds"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**jobs[job_id])

@router.get("/preview/{filename}")
async def preview_model(filename: str):
    """Proxy GLB file from GPU worker for browser preview"""
    # Extract job_id from filename (e.g., "abc-123.glb" -> "abc-123")
    job_id = filename.replace('.glb', '')
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    worker_job_id = job.get("worker_job_id")
    
    if not worker_job_id:
        raise HTTPException(status_code=500, detail="Worker job ID not found")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get GLB from worker
            worker_glb_url = f"{GPU_WORKER_URL}/outputs/{worker_job_id}/model.glb"
            logger.info(f"Proxying GLB preview from: {worker_glb_url}")
            response = await client.get(worker_glb_url)
            
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="model/gltf-binary",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "public, max-age=3600"
                    }
                )
            else:
                logger.error(f"Worker GLB fetch failed: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="GLB not available")
    except httpx.RequestError as e:
        logger.error(f"Preview proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Worker connection error: {str(e)}")

@router.get("/download/{job_id}")
async def download_model(job_id: str):
    """Download the generated 3D model - proxies full ZIP from GPU worker"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "complete":
        raise HTTPException(
            status_code=400,
            detail=f"Model not ready. Status: {job['status']}"
        )
    
    # Get worker job ID
    worker_job_id = job.get("worker_job_id")
    if not worker_job_id:
        raise HTTPException(status_code=500, detail="Worker job ID not found")
    
    # Proxy download from GPU worker (full ZIP with OBJ+MTL+textures)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            worker_download_url = f"{GPU_WORKER_URL}/download/{worker_job_id}"
            logger.info(f"Proxying download from: {worker_download_url}")
            response = await client.get(worker_download_url)
            
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/zip",
                    headers={
                        "Content-Disposition": f"attachment; filename=model_{job_id}.zip"
                    }
                )
            else:
                logger.error(f"Worker download failed: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to download from worker"
                )
    except httpx.RequestError as e:
        logger.error(f"Download proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Worker connection error: {str(e)}")

@router.get("/health")
async def gpu_health_check():
    """Health check for GPU model generation service"""
    worker_status = "unknown"
    worker_info = {}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GPU_WORKER_URL}/health")
            if response.status_code == 200:
                worker_status = "connected"
                worker_info = response.json()
    except Exception as e:
        worker_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "gpu_model_generation",
        "worker_url": GPU_WORKER_URL,
        "worker_status": worker_status,
        "worker_info": worker_info,
        "total_jobs": len(jobs),
        "active_jobs": len([j for j in jobs.values() if j["status"] in ["queued", "processing"]]),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }
