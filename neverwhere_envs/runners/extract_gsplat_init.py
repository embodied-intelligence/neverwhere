import argparse
import numpy as np
import trimesh
from PIL import Image

def load_mesh(ply_file, texture_file=None):
    mesh = trimesh.load(ply_file)
    vertices = mesh.vertices
    faces = mesh.faces
    print(f"Loaded mesh with {len(vertices)} vertices and {len(faces)} faces")
    
    texture = None
    if texture_file:
        texture = Image.open(texture_file)
    
    return mesh, texture

def transform_coordinate_system(vertices):
    transform_matrix = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    return np.dot(vertices, transform_matrix.T)

def get_vertex_colors(mesh, texture):
    if texture is None or not hasattr(mesh.visual, 'uv') or mesh.visual.uv is None:
        print("No texture or UV coordinates found. Using default grey color.")
        return np.full((len(mesh.vertices), 3), 0.5)

    uv = np.clip(mesh.visual.uv, 0, 1)
    x = (uv[:, 0] * (texture.width - 1)).astype(int)
    y = ((1 - uv[:, 1]) * (texture.height - 1)).astype(int)
    texture_array = np.array(texture)
    colors = texture_array[y, x, :3] / 255.0
    return colors

def write_colored_ply(file_path, vertices, colors):
    mesh = trimesh.Trimesh(vertices=vertices, vertex_colors=colors)
    mesh.export(file_path, file_type='ply')

def get_bounding_sphere(vertices):
    center = np.mean(vertices, axis=0)
    radius = np.max(np.linalg.norm(vertices - center, axis=1))
    return center, radius

def combine_point_clouds_with_sphere(vertices1, colors1, vertices2, colors2, sphere_ratio=0.8):
    center, radius = get_bounding_sphere(vertices1)
    sphere_radius = radius * sphere_ratio
    
    combined_vertices = vertices1
    combined_colors = colors1
    
    distances = np.linalg.norm(vertices2 - center, axis=1)
    outer_mask = distances > sphere_radius
    outer_vertices = vertices2[outer_mask]
    outer_colors = colors2[outer_mask]
    
    combined_vertices = np.vstack((combined_vertices, outer_vertices))
    combined_colors = np.vstack((combined_colors, outer_colors))
    
    return combined_vertices, combined_colors

def main():
    parser = argparse.ArgumentParser(description='Convert textured or non-textured mesh from OpenCV to OpenGL convention and export as colored point cloud')
    parser.add_argument('-i', '--input-file', required=True, help='Input PLY file')
    parser.add_argument('-t', '--texture-file', help='Input texture file (PNG, optional)')
    parser.add_argument('-o', '--output-file', required=True, help='Output PLY file')
    parser.add_argument('-c', '--combine', help='PLY file to combine with the converted point cloud')
    parser.add_argument('-r', '--sphere-ratio', type=float, default=0.8, help='Ratio of the bounding sphere radius to use for point selection (default: 0.8)')
    
    args = parser.parse_args()
    
    mesh, texture = load_mesh(args.input_file, args.texture_file)
    converted_vertices = transform_coordinate_system(mesh.vertices)
    colors = get_vertex_colors(mesh, texture)
    
    if args.combine:
        combine_mesh = trimesh.load(args.combine)
        combine_vertices = combine_mesh.vertices
        combine_colors = combine_mesh.visual.vertex_colors[:, :3] / 255.0
        
        final_vertices, final_colors = combine_point_clouds_with_sphere(
            converted_vertices, colors, combine_vertices, combine_colors, args.sphere_ratio
        )
    else:
        final_vertices, final_colors = converted_vertices, colors
    
    write_colored_ply(args.output_file, final_vertices, final_colors)
    print(f"Conversion complete. Output written to {args.output_file}")

if __name__ == "__main__":
    main()