from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/3d", tags=["3D Models"]) 

# Request/Response Models
class Generate3DModelRequest(BaseModel):
    prompt: str
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    style: Optional[str] = "realistic"
    complexity: Optional[str] = "medium"

class Generate3DModelResponse(BaseModel):
    model_id: str
    model_url: str
    status: str
    preview_url: Optional[str] = None
    estimated_time: Optional[int] = None

class Model3D(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    model_url: str
    preview_url: Optional[str] = None
    format: str
    file_size: Optional[int] = None
    created_at: str
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    status: str

# In-memory storage
models_db: dict[str, Model3D] = {}

@router.post("/generate", response_model=Generate3DModelResponse)
async def generate_3d_model(request: Generate3DModelRequest):
    """Generate a 3D model from a text prompt."""
    os.makedirs("static/models", exist_ok=True)
    model_id = str(uuid.uuid4())
    model_filename = f"{model_id}.glb"
    model_path = os.path.join("static", "models", model_filename)
    
    # Import your generator
    from utils.model_generator import generate_model_from_prompt
    
    try:
        generate_model_from_prompt(request.prompt, model_path)
        file_size = os.path.getsize(model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    
    model_url = f"/static/models/{model_filename}"
    
    model = Model3D(
        id=model_id,
        title=f"Generated: {request.prompt[:50]}",
        description=f"Generated from prompt: {request.prompt}",
        prompt=request.prompt,
        model_url=model_url,
        preview_url=None,
        format="glb",
        file_size=file_size,
        created_at=datetime.now().isoformat(),
        room_id=request.room_id,
        user_id=request.user_id,
        status="completed"
    )
    models_db[model_id] = model
    
    return Generate3DModelResponse(
        model_id=model_id,
        model_url=model_url,
        status="completed",
        preview_url=None,
        estimated_time=0
    )

@router.get("/models/{model_id}", response_model=Model3D)
async def get_3d_model(model_id: str):
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    return models_db[model_id]

@router.get("/models", response_model=List[Model3D])
async def list_3d_models(room_id: Optional[str] = None):
    if room_id:
        return [m for m in models_db.values() if m.room_id == room_id]
    return list(models_db.values())
