import os
import numpy as np
import trimesh
import open3d as o3d
from PIL import Image

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
    output_path = os.path.join(output_dir, 'openmvs_dense_colored.ply')
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

def process_visual_geometry(mesh_path, output_dir, simplify_factor=0.95):
    """Process mesh for collision geometry."""
    # Define output paths
    base_path = os.path.join(output_dir, 'visual_mesh.obj')
    base_simplified_path = os.path.join(output_dir, 'visual_mesh_simplified.obj')
    
    required_paths = [base_path, base_simplified_path]
    
    # Skip if all files exist
    if all(os.path.exists(p) for p in required_paths):
        print(f"Skipping visual geometry: all files already exist")
        return
    
    # Load original mesh with Open3D
    mesh = trimesh.load(mesh_path)
    # clear face and vertex normals
    new_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces)
    
    # Export original mesh
    if not os.path.exists(base_path):
        new_mesh.export(base_path)
        print(f"Saved collision geometry to {base_path}")
    
    # Simplify and export original mesh
    if not os.path.exists(base_simplified_path):
        mesh = trimesh.load(base_path)
        
        # Get connected components and keep only the largest one
        connected_components = mesh.split(only_watertight=False)
        if len(connected_components) > 1:
            # Find the component with the most faces
            largest_component = max(connected_components, key=lambda m: len(m.faces))
            mesh = largest_component
            print(f"Kept largest component with {len(mesh.faces)} faces out of {len(connected_components)} components")
        
        simplified_mesh = mesh.simplify_quadric_decimation(percent=simplify_factor)
        simplified_mesh.export(base_simplified_path)
        print(f"Saved simplified collision geometry to {base_simplified_path}")

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

def main(scene_dir, num_samples=100000, simplify_factor=0.95):
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
        textured_mesh_path = os.path.join(openmvs_dir, 'model_dense_recon_texture.ply')
        recon_path = os.path.join(openmvs_dir, 'model_dense_recon.ply')
        refine_path = os.path.join(openmvs_dir, 'model_dense_refine.ply')
        # recon mesh is in higher priority
        openmvs_mesh_path = recon_path if os.path.exists(recon_path) else refine_path
        
        if os.path.exists(textured_mesh_path):
            process_textured_mesh(textured_mesh_path, geometry_dir, num_samples=num_samples)
        
        if os.path.exists(openmvs_mesh_path):
            process_visual_geometry(openmvs_mesh_path, geometry_dir, simplify_factor=simplify_factor)
    
    # NOTE: this is used in previous version
    #       In current version, we use openmvs_dense_colored.ply as the initial point cloud, no sfm points needed
    # Combine point clouds
    # if os.path.exists(os.path.join(geometry_dir, 'pcd_colmap.ply')) and \
    #    os.path.exists(os.path.join(geometry_dir, 'pcd_openmvs_colored.ply')):
    #     combine_point_clouds(geometry_dir)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process geometry files for a scene')
    parser.add_argument('--scene-dir', required=True, help='Path to the scene directory')
    
    args = parser.parse_args()
    main(args.scene_dir)
