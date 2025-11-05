"""
3D Model Generation and Management API
Integrates Claude AI to generate 3D model descriptions and convert to GLB/GLTF
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid
import os
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/3d", tags=["3D Models"])

# In-memory storage for 3D models (replace with database in production)
models_db: Dict[str, Dict] = {}

# Ensure models directory exists
MODELS_DIR = os.path.join(os.getcwd(), "static", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# Request/Response Models
class Generate3DModelRequest(BaseModel):
    """Request to generate a 3D model from text prompt"""
    prompt: str
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    style: Optional[str] = "realistic"  # realistic, low-poly, stylized
    complexity: Optional[str] = "medium"  # simple, medium, complex


class Generate3DModelResponse(BaseModel):
    """Response after initiating 3D model generation"""
    model_id: str
    status: str  # 'processing', 'completed', 'failed'
    model_url: Optional[str] = None
    preview_url: Optional[str] = None
    estimated_time: Optional[int] = None  # seconds


class Model3D(BaseModel):
    """3D Model metadata"""
    id: str
    title: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    model_url: str
    preview_url: Optional[str] = None
    format: str  # 'glb' or 'gltf'
    file_size: Optional[int] = None
    created_at: str
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    status: str


# Claude AI Integration for 3D Description Generation
async def generate_3d_description_with_claude(prompt: str, style: str, complexity: str) -> Dict[str, Any]:
    """
    Use Claude AI to generate detailed 3D model description from user prompt.
    This description will be used to generate the actual 3D model.
    """
    from utils.claude_client import get_claude_client
    
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(
            status_code=503,
            detail="Claude AI not configured. Set ANTHROPIC_API_KEY environment variable."
        )
    
    # Build specialized prompt for 3D model generation
    system_prompt = f"""You are a 3D modeling expert assistant. Generate detailed 3D model specifications based on user descriptions.

Your response MUST be valid JSON with this exact structure:
{{
    "title": "Brief model name",
    "description": "Detailed description",
    "geometry": {{
        "primary_shape": "box|sphere|cylinder|custom",
        "dimensions": {{"width": 1.0, "height": 1.0, "depth": 1.0}},
        "components": [
            {{
                "type": "component name",
                "shape": "box|sphere|cylinder",
                "position": {{"x": 0, "y": 0, "z": 0}},
                "scale": {{"x": 1, "y": 1, "z": 1}},
                "rotation": {{"x": 0, "y": 0, "z": 0}},
                "color": "#RRGGBB"
            }}
        ]
    }},
    "materials": {{
        "base_color": "#RRGGBB",
        "metallic": 0.5,
        "roughness": 0.5,
        "emissive": "#000000"
    }},
    "style": "{style}",
    "complexity": "{complexity}"
}}

Guidelines:
- Break complex objects into multiple components
- Use realistic proportions and positioning
- Specify colors in hex format (#RRGGBB)
- Position components relative to center (0,0,0)
- Scale values are multipliers (1.0 = normal size)
- Rotation in degrees (0-360)

Style={style}, Complexity={complexity}
"""

    user_prompt = f"Generate a 3D model specification for: {prompt}"
    
    try:
        # Generate with Claude
        response = await claude.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.7
        )
        
        # Extract JSON from response (Claude might wrap it in markdown)
        json_str = response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()
        
        # Parse JSON
        model_spec = json.loads(json_str)
        
        logger.info(f"Generated 3D model specification: {model_spec.get('title')}")
        return model_spec
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        logger.error(f"Response was: {response}")
        # Return fallback specification
        return {
            "title": prompt[:50],
            "description": f"Basic model based on: {prompt}",
            "geometry": {
                "primary_shape": "box",
                "dimensions": {"width": 1.0, "height": 1.0, "depth": 1.0},
                "components": []
            },
            "materials": {
                "base_color": "#4A90E2",
                "metallic": 0.3,
                "roughness": 0.7,
                "emissive": "#000000"
            },
            "style": style,
            "complexity": complexity
        }
    except Exception as e:
        logger.error(f"Error generating 3D description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate model description: {str(e)}")


# 3D Model Generation (Procedural GLB Creation)
def create_glb_from_specification(spec: Dict[str, Any], output_path: str) -> str:
    """
    Create a GLB file from the Claude-generated specification.
    Uses trimesh for procedural geometry generation.
    """
    try:
        import trimesh
        import numpy as np
        
        # Create scene
        scene = trimesh.Scene()
        
        # Extract geometry info
        geometry = spec.get("geometry", {})
        materials = spec.get("materials", {})
        components = geometry.get("components", [])
        
        # Helper function to create basic shapes
        def create_shape(shape_type: str, scale: Dict = None):
            scale = scale or {"x": 1, "y": 1, "z": 1}
            
            if shape_type == "box":
                mesh = trimesh.creation.box(extents=[scale["x"], scale["y"], scale["z"]])
            elif shape_type == "sphere":
                mesh = trimesh.creation.icosphere(subdivisions=2, radius=0.5)
                mesh.apply_scale([scale["x"], scale["y"], scale["z"]])
            elif shape_type == "cylinder":
                mesh = trimesh.creation.cylinder(radius=0.5, height=scale["y"])
                mesh.apply_scale([scale["x"], 1.0, scale["z"]])
            else:
                # Default to box
                mesh = trimesh.creation.box(extents=[scale["x"], scale["y"], scale["z"]])
            
            return mesh
        
        # If no components, create primary shape
        if not components:
            primary_shape = geometry.get("primary_shape", "box")
            dimensions = geometry.get("dimensions", {"width": 1, "height": 1, "depth": 1})
            scale = {
                "x": dimensions.get("width", 1),
                "y": dimensions.get("height", 1),
                "z": dimensions.get("depth", 1)
            }
            mesh = create_shape(primary_shape, scale)
            
            # Apply color
            base_color = materials.get("base_color", "#4A90E2")
            color = [int(base_color[i:i+2], 16) for i in (1, 3, 5)] + [255]
            mesh.visual.vertex_colors = color
            
            scene.add_geometry(mesh)
        else:
            # Create each component
            for i, component in enumerate(components):
                comp_shape = component.get("shape", "box")
                comp_scale = component.get("scale", {"x": 1, "y": 1, "z": 1})
                comp_position = component.get("position", {"x": 0, "y": 0, "z": 0})
                comp_rotation = component.get("rotation", {"x": 0, "y": 0, "z": 0})
                comp_color = component.get("color", materials.get("base_color", "#4A90E2"))
                
                # Create mesh
                mesh = create_shape(comp_shape, comp_scale)
                
                # Apply color
                color = [int(comp_color[i:i+2], 16) for i in (1, 3, 5)] + [255]
                mesh.visual.vertex_colors = color
                
                # Apply transformations
                mesh.apply_translation([comp_position["x"], comp_position["y"], comp_position["z"]])
                
                # Apply rotation (convert degrees to radians)
                if comp_rotation["x"] != 0:
                    mesh.apply_transform(trimesh.transformations.rotation_matrix(
                        np.radians(comp_rotation["x"]), [1, 0, 0]))
                if comp_rotation["y"] != 0:
                    mesh.apply_transform(trimesh.transformations.rotation_matrix(
                        np.radians(comp_rotation["y"]), [0, 1, 0]))
                if comp_rotation["z"] != 0:
                    mesh.apply_transform(trimesh.transformations.rotation_matrix(
                        np.radians(comp_rotation["z"]), [0, 0, 1]))
                
                scene.add_geometry(mesh, node_name=f"component_{i}")
        
        # Export to GLB
        scene.export(output_path, file_type='glb')
        logger.info(f"Created GLB file: {output_path}")
        
        return output_path
        
    except ImportError:
        logger.error("trimesh not installed. Install with: pip install trimesh")
        raise HTTPException(
            status_code=500,
            detail="3D generation library not available. Install trimesh: pip install trimesh"
        )
    except Exception as e:
        logger.error(f"Error creating GLB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create 3D model: {str(e)}")


# API Endpoints
@router.post("/generate", response_model=Generate3DModelResponse)
async def generate_3d_model(request: Generate3DModelRequest):
    """
    Generate a 3D model from a text prompt using Claude AI.
    
    Example:
        POST /api/v1/3d/generate
        {
            "prompt": "A futuristic drone with four propellers",
            "style": "realistic",
            "complexity": "medium"
        }
    """
    try:
        model_id = str(uuid.uuid4())
        
        logger.info(f"Generating 3D model: {request.prompt}")
        
        # Step 1: Generate model specification with Claude
        spec = await generate_3d_description_with_claude(
            request.prompt,
            request.style or "realistic",
            request.complexity or "medium"
        )
        
        # Step 2: Create GLB file from specification
        filename = f"{model_id}.glb"
        output_path = os.path.join(MODELS_DIR, filename)
        
        create_glb_from_specification(spec, output_path)
        
        # Step 3: Get file size
        file_size = os.path.getsize(output_path)
        
        # Step 4: Store in database
        model_data = {
            "id": model_id,
            "title": spec.get("title", request.prompt[:50]),
            "description": spec.get("description"),
            "prompt": request.prompt,
            "model_url": f"/static/models/{filename}",
            "format": "glb",
            "file_size": file_size,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "room_id": request.room_id,
            "user_id": request.user_id,
            "status": "completed",
            "specification": spec  # Store Claude's specification
        }
        
        models_db[model_id] = model_data
        
        logger.info(f"Successfully generated 3D model: {model_id}")
        
        return Generate3DModelResponse(
            model_id=model_id,
            status="completed",
            model_url=f"/static/models/{filename}",
            estimated_time=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating 3D model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}", response_model=Model3D)
async def get_3d_model(model_id: str):
    """Get 3D model metadata by ID"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models_db[model_id]
    return Model3D(**model)


@router.get("/models", response_model=List[Model3D])
async def list_3d_models(
    room_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50
):
    """List all 3D models, optionally filtered by room or user"""
    all_models = list(models_db.values())
    
    # Apply filters
    if room_id:
        all_models = [m for m in all_models if m.get("room_id") == room_id]
    if user_id:
        all_models = [m for m in all_models if m.get("user_id") == user_id]
    
    # Sort by created_at descending
    all_models.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Apply limit
    all_models = all_models[:limit]
    
    return [Model3D(**m) for m in all_models]


@router.delete("/models/{model_id}")
async def delete_3d_model(model_id: str):
    """Delete a 3D model"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models_db[model_id]
    
    # Delete file
    model_url = model.get("model_url", "")
    if model_url.startswith("/static/models/"):
        filename = model_url.replace("/static/models/", "")
        file_path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
    
    # Delete from database
    del models_db[model_id]
    
    return {"message": "Model deleted successfully"}


@router.get("/health")
async def model_3d_health():
    """Check 3D model generation service health"""
    from utils.claude_client import get_claude_client
    
    claude = get_claude_client()
    
    try:
        import trimesh
        trimesh_available = True
    except ImportError:
        trimesh_available = False
    
    return {
        "status": "healthy",
        "claude_enabled": claude.is_enabled,
        "trimesh_available": trimesh_available,
        "models_count": len(models_db),
        "features": {
            "ai_description_generation": claude.is_enabled,
            "procedural_modeling": trimesh_available,
            "glb_export": trimesh_available
        }
    }
