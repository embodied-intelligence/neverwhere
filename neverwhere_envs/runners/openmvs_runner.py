import os
import subprocess
import argparse

def bash_run(cmd):
    # Assuming OpenMVS is installed and in PATH
    print('\nRunning cmd: ', cmd)
    subprocess.check_call(['/bin/bash', '-c', cmd])
    
def run_interface_colmap(colmap_dir, output_mvs, working_dir, image_dir, gpu_index='-1'):
    print('Running COLMAP interface...')
    cmd = f'InterfaceCOLMAP -w {working_dir} -i {colmap_dir} -o {output_mvs}'
    bash_run(cmd)
    
    # Create symlink for images using provided image_dir
    images_link = os.path.join(working_dir, 'images')
    if not os.path.exists(images_link):
        os.symlink(image_dir, images_link)

def run_densify(input_mvs, output_mvs, working_dir, gpu_index='-1', verbose=1):
    print('Running point cloud densification...')
    cmd = f'DensifyPointCloud -i {input_mvs} \
        -o {output_mvs} \
        -w {working_dir} \
        --resolution-level 0 \
        --max-resolution 256 \
        --cuda-device {gpu_index} \
        -v {verbose}'
    bash_run(cmd)

def run_reconstruct(input_mvs, output_mvs, point_cloud, working_dir, gpu_index='-1'):
    print('Running mesh reconstruction...')
    cmd = f'ReconstructMesh -i {input_mvs} \
        -p {point_cloud} \
        -o {output_mvs} \
        -w {working_dir} \
        --cuda-device {gpu_index}'
    bash_run(cmd)

def run_refine(input_mvs, input_mesh, output_mvs, working_dir, gpu_index='-1', scales=1, max_face_area=16):
    print('Running mesh refinement...')
    cmd = f'RefineMesh -i {input_mvs} \
        -m {input_mesh} \
        -o {output_mvs} \
        -w {working_dir} \
        --scales {scales} \
        --max-face-area {max_face_area} \
        --cuda-device {gpu_index}'
    bash_run(cmd)

def run_texture(input_mvs, input_mesh, output_mvs, working_dir, gpu_index='-1', decimate=0.1, resolution_level=2):
    print('Running mesh texturing...')
    cmd = f'TextureMesh {input_mvs} \
        -m {input_mesh} \
        -o {output_mvs} \
        -w {working_dir} \
        --cuda-device {gpu_index} \
        --decimate {decimate} \
        --resolution-level {resolution_level}'
    bash_run(cmd)

def main(working_dir, colmap_dir, image_dir, gpu_index='-1'):
    """
    Run OpenMVS pipeline
    Args:
        working_dir: Directory containing all working files
        colmap_dir: Path to COLMAP output directory
        image_dir: Directory containing input images
        gpu_index: GPU index to use for OpenMVS commands
    """
    os.makedirs(working_dir, exist_ok=True)

    # Define file paths
    colmap_mvs = os.path.join(working_dir, 'model_colmap.mvs')
    dense_mvs = os.path.join(working_dir, 'model_dense.mvs')
    dense_ply = os.path.join(working_dir, 'model_dense.ply')
    recon_mvs = os.path.join(working_dir, 'model_dense_recon.mvs')
    recon_ply = os.path.join(working_dir, 'model_dense_recon.ply')
    refine_mvs = os.path.join(working_dir, 'model_dense_mesh_refine.mvs')
    refine_ply = os.path.join(working_dir, 'model_dense_mesh_refine.ply')
    texture_mvs = os.path.join(working_dir, 'model_dense_mesh_refine_texture.mvs')

    # Run pipeline with GPU index for all steps
    run_interface_colmap(colmap_dir, colmap_mvs, working_dir, image_dir, gpu_index)
    run_densify(colmap_mvs, dense_mvs, working_dir, gpu_index)
    run_reconstruct(dense_mvs, recon_mvs, dense_ply, working_dir, gpu_index)
    run_refine(dense_mvs, recon_ply, refine_mvs, working_dir, gpu_index)
    run_texture(dense_mvs, refine_ply, texture_mvs, working_dir, gpu_index, decimate=0.1, resolution_level=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run OpenMVS pipeline')
    parser.add_argument('--working-dir', type=str, required=True,
                      help='Directory for OpenMVS working files')
    parser.add_argument('--colmap-dir', type=str, required=True,
                      help='Path to COLMAP output directory')
    parser.add_argument('--img-dir', type=str, required=True,
                      help='Directory containing input images')
    parser.add_argument('--gpu-index', type=str, default='-1',
                      help='GPU index to use for OpenMVS commands')
    
    args = parser.parse_args()
    
    # Run the OpenMVS pipeline
    main(
        working_dir=args.working_dir,
        colmap_dir=args.colmap_dir,
        image_dir=args.img_dir,
        gpu_index=args.gpu_index
    )
