import argparse
import trimesh
import os
import numpy as np

def load_ply(ply_file):
    mesh = trimesh.load(ply_file)
    print(f"Loaded PLY mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
    return mesh

def write_obj(file_path, mesh):
    # Check if the directory exists, if not, create it
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        # Write vertices
        np.savetxt(f, mesh.vertices, fmt='v %f %f %f')
        
        # Write normals if they exist
        if mesh.vertex_normals is not None:
            np.savetxt(f, mesh.vertex_normals, fmt='vn %f %f %f')
        
        # Prepare face data
        if mesh.vertex_normals is not None:
            face_data = np.column_stack((mesh.faces + 1, mesh.faces + 1))
            face_format = 'f %d//%d %d//%d %d//%d'
        else:
            face_data = mesh.faces + 1
            face_format = 'f %d %d %d'
        
        # Write faces
        np.savetxt(f, face_data, fmt=face_format)
    
    print(f"OBJ file written to {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert PLY mesh file to OBJ format')
    parser.add_argument('-i', '--input-file', required=True, help='Input PLY file')
    parser.add_argument('-o', '--output-file', required=True, help='Output OBJ file')
    
    args = parser.parse_args()
    
    mesh = load_ply(args.input_file)
    write_obj(args.output_file, mesh)
    print(f"Conversion complete. OBJ file written to {args.output_file}")

if __name__ == "__main__":
    main()