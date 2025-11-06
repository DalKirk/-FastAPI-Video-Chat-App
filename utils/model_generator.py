import trimesh
import numpy as np
import os

def generate_simple_cube(size: float = 1.0) -> trimesh.Trimesh:
    return trimesh.creation.box(extents=[size, size, size])

def generate_simple_sphere(radius: float = 1.0, subdivisions: int = 3) -> trimesh.Trimesh:
    return trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)

def generate_simple_cylinder(radius: float = 0.5, height: float = 2.0) -> trimesh.Trimesh:
    return trimesh.creation.cylinder(radius=radius, height=height)

def generate_simple_cone(radius: float = 0.5, height: float = 2.0) -> trimesh.Trimesh:
    return trimesh.creation.cone(radius=radius, height=height)

def generate_simple_torus(major_radius: float = 1.0, minor_radius: float = 0.3) -> trimesh.Trimesh:
    return trimesh.creation.torus(major_radius=major_radius, minor_radius=minor_radius)

def generate_capsule(radius: float = 0.5, height: float = 2.0) -> trimesh.Trimesh:
    return trimesh.creation.capsule(radius=radius, height=height)

def generate_model_from_prompt(prompt: str, output_path: str) -> str:
    """
    Generate a 3D model based on a text prompt.
    Enhanced keyword matching with better shape detection and simple compositions.
    """
    prompt_lower = prompt.lower()

    # Animal/Character shapes - approximate with primitives
    if any(word in prompt_lower for word in ["cat", "dog", "animal", "pet"]):
        # Simple cat/dog approximation: body (cylinder) + head (sphere)
        body = generate_simple_cylinder(radius=0.4, height=1.2)
        head = generate_simple_sphere(radius=0.5, subdivisions=2)
        head.apply_translation([0, 0, 1.0])
        mesh = trimesh.util.concatenate([body, head])

    elif any(word in prompt_lower for word in ["person", "human", "character"]):
        # Simple humanoid: body + head
        body = generate_simple_cylinder(radius=0.3, height=1.5)
        head = generate_simple_sphere(radius=0.3, subdivisions=2)
        head.apply_translation([0, 0, 1.2])
        mesh = trimesh.util.concatenate([body, head])

    # Basic shapes
    elif any(word in prompt_lower for word in ["cube", "box", "square"]):
        mesh = generate_simple_cube()

    elif any(word in prompt_lower for word in ["sphere", "ball", "circle", "orb"]):
        mesh = generate_simple_sphere()

    elif any(word in prompt_lower for word in ["cylinder", "tube", "pipe"]):
        mesh = generate_simple_cylinder()

    elif any(word in prompt_lower for word in ["cone", "pyramid", "triangle"]):
        mesh = generate_simple_cone()

    elif any(word in prompt_lower for word in ["torus", "ring", "donut", "doughnut"]):
        mesh = generate_simple_torus()

    elif any(word in prompt_lower for word in ["capsule", "pill"]):
        mesh = generate_capsule()

    # Objects
    elif any(word in prompt_lower for word in ["table", "desk"]):
        # Simple table: top (cube) + legs (cylinders)
        top = generate_simple_cube(size=2.0)
        top.apply_scale([1.0, 1.0, 0.1])
        top.apply_translation([0, 0, 0.7])

        leg1 = generate_simple_cylinder(radius=0.05, height=0.7)
        leg2 = leg1.copy()
        leg3 = leg1.copy()
        leg4 = leg1.copy()

        leg1.apply_translation([0.9, 0.9, 0])
        leg2.apply_translation([0.9, -0.9, 0])
        leg3.apply_translation([-0.9, 0.9, 0])
        leg4.apply_translation([-0.9, -0.9, 0])

        mesh = trimesh.util.concatenate([top, leg1, leg2, leg3, leg4])

    elif any(word in prompt_lower for word in ["chair", "seat"]):
        # Simple chair: seat + back
        seat = generate_simple_cube(size=1.0)
        seat.apply_scale([1.0, 1.0, 0.1])
        seat.apply_translation([0, 0, 0.45])
        back = generate_simple_cube(size=1.0)
        back.apply_scale([1.0, 0.1, 1.0])
        back.apply_translation([0, -0.45, 0.95])
        mesh = trimesh.util.concatenate([seat, back])

    elif any(word in prompt_lower for word in ["tree", "plant"]):
        # Simple tree: trunk + crown
        trunk = generate_simple_cylinder(radius=0.2, height=2.0)
        crown = generate_simple_sphere(radius=1.0)
        crown.apply_translation([0, 0, 2.5])
        mesh = trimesh.util.concatenate([trunk, crown])

    elif any(word in prompt_lower for word in ["house", "building"]):
        # Simple house: base + roof
        base = generate_simple_cube(size=2.0)
        roof = generate_simple_cone(radius=1.5, height=1.0)
        roof.apply_translation([0, 0, 1.5])
        mesh = trimesh.util.concatenate([base, roof])

    elif any(word in prompt_lower for word in ["car", "vehicle", "truck"]):
        # Simple car: body + cabin
        body = generate_simple_cube(size=2.0)
        body.apply_scale([1.5, 0.8, 0.5])
        cabin = generate_simple_cube(size=1.0)
        cabin.apply_scale([0.8, 0.8, 0.6])
        cabin.apply_translation([0, 0, 0.55])
        mesh = trimesh.util.concatenate([body, cabin])

    else:
        # Default: sphere (more interesting than cube)
        mesh = generate_simple_sphere()

    # Apply colors based on keywords
    if "red" in prompt_lower:
        mesh.visual.vertex_colors = [255, 0, 0, 255]
    elif "blue" in prompt_lower:
        mesh.visual.vertex_colors = [0, 0, 255, 255]
    elif "green" in prompt_lower:
        mesh.visual.vertex_colors = [0, 255, 0, 255]
    elif "yellow" in prompt_lower:
        mesh.visual.vertex_colors = [255, 255, 0, 255]
    elif "purple" in prompt_lower:
        mesh.visual.vertex_colors = [128, 0, 128, 255]
    elif "orange" in prompt_lower:
        mesh.visual.vertex_colors = [255, 165, 0, 255]
    elif "pink" in prompt_lower:
        mesh.visual.vertex_colors = [255, 192, 203, 255]
    elif "brown" in prompt_lower:
        mesh.visual.vertex_colors = [139, 69, 19, 255]
    elif "white" in prompt_lower:
        mesh.visual.vertex_colors = [255, 255, 255, 255]
    elif "black" in prompt_lower:
        mesh.visual.vertex_colors = [0, 0, 0, 255]
    elif "gray" in prompt_lower or "grey" in prompt_lower:
        mesh.visual.vertex_colors = [128, 128, 128, 255]
    else:
        # Default color: light gray
        mesh.visual.vertex_colors = [200, 200, 200, 255]

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Export as GLB
    mesh.export(output_path, file_type='glb')
    return output_path
