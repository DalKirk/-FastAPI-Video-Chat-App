import trimesh
import numpy as np
import os

def generate_simple_cube(size: float = 1.0) -> trimesh.Trimesh:
    return trimesh.creation.box(extents=[size, size, size])

def generate_simple_sphere(radius: float = 1.0, subdivisions: int = 3) -> trimesh.Trimesh:
    return trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)

def generate_simple_cylinder(radius: float = 0.5, height: float = 2.0) -> trimesh.Trimesh:
    return trimesh.creation.cylinder(radius=radius, height=height)

def generate_model_from_prompt(prompt: str, output_path: str) -> str:
    """Generate a 3D model based on text prompt."""
    prompt_lower = prompt.lower()
    
    # Keyword matching
    if "cube" in prompt_lower or "box" in prompt_lower:
        mesh = generate_simple_cube()
    elif "sphere" in prompt_lower or "ball" in prompt_lower:
        mesh = generate_simple_sphere()
    elif "cylinder" in prompt_lower or "tube" in prompt_lower:
        mesh = generate_simple_cylinder()
    else:
        mesh = generate_simple_cube()
    
    # Apply colors
    if "red" in prompt_lower:
        mesh.visual.vertex_colors = [255, 0, 0, 255]
    elif "blue" in prompt_lower:
        mesh.visual.vertex_colors = [0, 0, 255, 255]
    elif "green" in prompt_lower:
        mesh.visual.vertex_colors = [0, 255, 0, 255]
    elif "yellow" in prompt_lower:
        mesh.visual.vertex_colors = [255, 255, 0, 255]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Export as GLB
    mesh.export(output_path, file_type='glb')
    return output_path
