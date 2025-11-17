from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter(prefix="/static/models/gpu", tags=["Static Models"])

MODELS_DIR = Path("static/models/gpu")

@router.get("/{filename}")
async def serve_model_file(filename: str):
    """Serve GLB files with proper content type and CORS headers"""
    file_path = MODELS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Model file not found")
    
    # Determine content type
    if filename.endswith('.glb'):
        media_type = "model/gltf-binary"
    elif filename.endswith('.gltf'):
        media_type = "model/gltf+json"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "public, max-age=31536000"
        }
    )
