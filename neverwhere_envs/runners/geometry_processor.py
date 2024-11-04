import os
import numpy as np
import open3d as o3d
from PIL import Image
import subprocess
import shutil

def read_points3D_text(path):
    """Read points3D.txt file and return points and colors."""
    points3D = {}
    
    with open(path, "r") as fid:
        while True:
            line = fid.readline()
            if not line:
                break
            line = line.strip()
            if len(line) > 0 and line[0] != "#":
                elems = line.split()
                point_id = int(elems[0])
                xyz = np.array(tuple(map(float, elems[1:4])))
                rgb = np.array(tuple(map(int, elems[4:7])))
                # error = float(elems[7])
                # track_length = int(len(elems[8:]) / 2)
                points3D[point_id] = (xyz, rgb)
    
    # Convert to numpy arrays
    if points3D:
        points = np.stack([p[0] for p in points3D.values()])
        colors = np.stack([p[1] for p in points3D.values()]).astype(np.float32) / 255.0
    else:
        points = np.zeros((0, 3))
        colors = np.zeros((0, 3))
    
    return points, colors

def extract_colmap_points(colmap_dir, output_dir):
    """Extract COLMAP points from TXT files and save as PLY."""
    output_path = os.path.join(output_dir, 'pcd_colmap.ply')
    if os.path.exists(output_path):
        print(f"Skipping COLMAP point cloud: {output_path} already exists")
        return
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read points3D.txt file
    points3D_path = os.path.join(colmap_dir, 'sparse', 'points3D.txt')
    if not os.path.exists(points3D_path):
        print(f"Warning: Could not find points3D.txt at {points3D_path}")
        return
    
    # Read points and colors
    points, colors = read_points3D_text(points3D_path)
    
    # Create and save point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    output_path = os.path.join(output_dir, 'pcd_colmap.ply')
    o3d.io.write_point_cloud(output_path, pcd)
    print(f"Saved COLMAP point cloud to {output_path}")

def process_textured_mesh(mesh_path, output_dir, num_samples=100000):
    """Convert textured mesh to colored point cloud with sampling."""
    output_path = os.path.join(output_dir, 'pcd_openmvs_colored.ply')
    if os.path.exists(output_path):
        print(f"Skipping sampled point cloud: {output_path} already exists")
        return
    
    # Load mesh and texture
    mesh = trimesh.load(mesh_path)
    texture_path = mesh_path.replace('.ply', '0.png')
    
    if os.path.exists(texture_path):
        texture = Image.open(texture_path)
    else:
        print(f"Warning: Texture file not found at {texture_path}")
        texture = None

    # Sample points from the mesh surface
    vertices, face_indices = trimesh.sample.sample_surface(mesh, num_samples)
    
    # Get colors for sampled points
    if texture is not None and hasattr(mesh.visual, 'uv'):
        # Get UV coordinates for sampled points by interpolating face UVs
        face_uvs = mesh.visual.uv[mesh.faces[face_indices]]
        # Generate random barycentric coordinates
        barycentric = np.random.dirichlet((1, 1, 1), size=num_samples)
        # Interpolate UV coordinates using barycentric coordinates
        uv = np.sum(face_uvs * barycentric[:, :, np.newaxis], axis=1)
        
        # Sample colors from texture
        uv = np.clip(uv, 0, 1)
        x = (uv[:, 0] * (texture.width - 1)).astype(int)
        y = ((1 - uv[:, 1]) * (texture.height - 1)).astype(int)
        texture_array = np.array(texture)
        colors = texture_array[y, x, :3] / 255.0
    else:
        colors = np.full((num_samples, 3), 0.5)

    # Create and save colored point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(vertices)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    output_path = os.path.join(output_dir, 'pcd_openmvs_colored.ply')
    o3d.io.write_point_cloud(output_path, pcd)
    print(f"Saved sampled point cloud ({num_samples} points) to {output_path}")
    
def invert_mesh(mesh):
    """
    Inverts a mesh by flipping its faces.
    
    Args:
        mesh: An open3d.geometry.TriangleMesh object
        
    Returns:
        open3d.geometry.TriangleMesh: Inverted mesh with flipped faces
    """
    # Create a copy of the mesh to avoid modifying the original
    inverted_mesh = o3d.geometry.TriangleMesh()
    inverted_mesh.vertices = mesh.vertices
    # Flip the triangle indices to invert the mesh
    triangles = np.asarray(mesh.triangles)
    inverted_mesh.triangles = o3d.utility.Vector3iVector(np.flip(triangles, axis=1))
    inverted_mesh.compute_vertex_normals()
    return inverted_mesh

def process_collision_geometry(mesh_path, output_dir, export_invert=False):
    """Process mesh for collision geometry."""
    # Define output paths
    base_path = os.path.join(output_dir, 'collision.obj')
    base_simplified_path = os.path.join(output_dir, 'collision_simplified.obj')
    
    if export_invert:
        inverted_path = os.path.join(output_dir, 'collision_inverted.obj')
        inverted_simplified_path = os.path.join(output_dir, 'collision_inverted_simplified.obj')
        required_paths = [base_path, inverted_path, base_simplified_path, inverted_simplified_path]
    else:
        required_paths = [base_path, base_simplified_path]
    
    # Skip if all files exist
    if all(os.path.exists(p) for p in required_paths):
        print(f"Skipping collision geometry: all files already exist")
        return
    
    # Load original mesh with Open3D
    mesh = o3d.io.read_triangle_mesh(mesh_path)
    
    # Create inverted mesh if needed
    if export_invert:
        inverted_mesh = invert_mesh(mesh)
    
    # Export original mesh
    if not os.path.exists(base_path):
        o3d.io.write_triangle_mesh(base_path, mesh)
        print(f"Saved collision geometry to {base_path}")
    
    # Export inverted mesh if needed
    if export_invert and not os.path.exists(inverted_path):
        o3d.io.write_triangle_mesh(inverted_path, inverted_mesh)
        print(f"Saved inverted collision geometry to {inverted_path}")
    
    # Simplify meshes (reduce to ~20% of original faces)
    target_faces = max(len(np.asarray(mesh.triangles)) // 5, 1000)  # Minimum 1000 faces
    
    # Simplify and export original mesh
    if not os.path.exists(base_simplified_path):
        simplified_mesh = mesh.simplify_quadric_decimation(target_faces)
        o3d.io.write_triangle_mesh(base_simplified_path, simplified_mesh)
        print(f"Saved simplified collision geometry to {base_simplified_path}")
    
    # Simplify and export inverted mesh if needed
    if export_invert and not os.path.exists(inverted_simplified_path):
        simplified_inverted = inverted_mesh.simplify_quadric_decimation(target_faces)
        o3d.io.write_triangle_mesh(inverted_simplified_path, simplified_inverted)
        print(f"Saved simplified inverted collision geometry to {inverted_simplified_path}")

def combine_point_clouds(output_dir, sphere_ratio=0.8):
    """Combine COLMAP and OpenMVS point clouds."""
    output_path = os.path.join(output_dir, 'pcd_gsplat_init.ply')
    if os.path.exists(output_path):
        print(f"Skipping combined point cloud: {output_path} already exists")
        return
    
    colmap_pcd = o3d.io.read_point_cloud(os.path.join(output_dir, 'pcd_colmap.ply'))
    openmvs_pcd = o3d.io.read_point_cloud(os.path.join(output_dir, 'pcd_openmvs_colored.ply'))
    
    # Get vertices and colors
    vertices1 = np.asarray(openmvs_pcd.points)
    colors1 = np.asarray(openmvs_pcd.colors)
    vertices2 = np.asarray(colmap_pcd.points)
    colors2 = np.asarray(colmap_pcd.colors)
    
    # Calculate bounding sphere
    center = np.mean(vertices1, axis=0)
    radius = np.max(np.linalg.norm(vertices1 - center, axis=1))
    sphere_radius = radius * sphere_ratio
    
    # Combine point clouds
    distances = np.linalg.norm(vertices2 - center, axis=1)
    outer_mask = distances > sphere_radius
    outer_vertices = vertices2[outer_mask]
    outer_colors = colors2[outer_mask]
    
    combined_vertices = np.vstack((vertices1, outer_vertices))
    combined_colors = np.vstack((colors1, outer_colors))
    
    # Create and save combined point cloud
    combined_pcd = o3d.geometry.PointCloud()
    combined_pcd.points = o3d.utility.Vector3dVector(combined_vertices)
    combined_pcd.colors = o3d.utility.Vector3dVector(combined_colors)
    
    output_path = os.path.join(output_dir, 'pcd_gsplat_init.ply')
    o3d.io.write_point_cloud(output_path, combined_pcd)
    print(f"Saved combined point cloud to {output_path}")

def process_scene(scene_dir):
    """Process all geometry files for a scene."""
    # Create geometry directory
    geometry_dir = os.path.join(scene_dir, 'geometry')
    os.makedirs(geometry_dir, exist_ok=True)
    
    # Process COLMAP points
    colmap_dir = os.path.join(scene_dir, 'colmap')
    if os.path.exists(colmap_dir):
        extract_colmap_points(colmap_dir, geometry_dir)
    
    # Process OpenMVS files
    openmvs_dir = os.path.join(scene_dir, 'openmvs')
    if os.path.exists(openmvs_dir):
        textured_mesh_path = os.path.join(openmvs_dir, 'model_dense_mesh_refine_texture.ply')
        collision_mesh_path = os.path.join(openmvs_dir, 'model_dense_mesh_refine.ply')
        
        if os.path.exists(textured_mesh_path):
            process_textured_mesh(textured_mesh_path, geometry_dir)
        
        if os.path.exists(collision_mesh_path):
            process_collision_geometry(collision_mesh_path, geometry_dir)
    
    # Combine point clouds
    if os.path.exists(os.path.join(geometry_dir, 'pcd_colmap.ply')) and \
       os.path.exists(os.path.join(geometry_dir, 'pcd_openmvs_colored.ply')):
        combine_point_clouds(geometry_dir)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process geometry files for a scene')
    parser.add_argument('--scene-dir', required=True, help='Path to the scene directory')
    
    args = parser.parse_args()
    process_scene(args.scene_dir)
