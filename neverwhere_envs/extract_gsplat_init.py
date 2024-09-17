import argparse
import numpy as np
import trimesh
from PIL import Image

def load_textured_mesh(ply_file, texture_file):
    # Load the mesh
    mesh = trimesh.load(ply_file)
    
    # Load the texture
    texture = Image.open(texture_file)
    
    # Get vertices and faces
    vertices = mesh.vertices
    faces = mesh.faces
    
    print(f"Loaded mesh with {len(vertices)} vertices and {len(faces)} faces")
    
    return mesh, texture

def transform_coordinate_system(vertices):
    # Define the transformation matrix directly
    transform_matrix = np.array([
        [1,  0,  0],
        [0,  0,  1],
        [0, -1,  0]
    ])
    
    # Apply the transformation
    return np.dot(vertices, transform_matrix.T)

def get_vertex_colors(mesh, texture):
    if not hasattr(mesh.visual, 'uv') or mesh.visual.uv is None:
        print("Warning: No texture coordinates found. Using default color.")
        return np.full((len(mesh.vertices), 3), 0.5)  # Default gray color
    
    # Get the UV coordinates
    uv = mesh.visual.uv
    
    # Ensure UV coordinates are within [0, 1] range
    uv = np.clip(uv, 0, 1)
    
    # Calculate pixel coordinates
    x = (uv[:, 0] * (texture.width - 1)).astype(int)
    y = ((1 - uv[:, 1]) * (texture.height - 1)).astype(int)  # Flip y-coordinate
    
    # Convert texture to numpy array for faster access
    texture_array = np.array(texture)
    
    # Sample the texture
    colors = texture_array[y, x, :3] / 255.0  # Normalize to [0, 1]
    
    return colors

def write_colored_ply(file_path, vertices, colors):
    # Create a new trimesh object with vertices and colors
    mesh = trimesh.Trimesh(vertices=vertices, vertex_colors=colors)
    
    # Export as PLY
    mesh.export(file_path, file_type='ply')

def main():
    parser = argparse.ArgumentParser(description='Convert textured mesh from OpenCV to OpenGL convention and export as colored point cloud')
    parser.add_argument('-i', '--input-file', required=True, help='Input PLY file')
    parser.add_argument('-t', '--texture-file', required=True, help='Input texture file (PNG)')
    parser.add_argument('-o', '--output-file', required=True, help='Output PLY file')
    
    args = parser.parse_args()
    
    # Load textured mesh
    mesh, texture = load_textured_mesh(args.input_file, args.texture_file)
    
    # Convert vertices to OpenGL coordinate system
    converted_vertices = transform_coordinate_system(mesh.vertices)
    
    # Get vertex colors
    colors = get_vertex_colors(mesh, texture)
    
    # Write converted vertices and colors to PLY file
    write_colored_ply(args.output_file, converted_vertices, colors)
    
    print(f"Conversion complete. Output written to {args.output_file}")

if __name__ == "__main__":
    main()