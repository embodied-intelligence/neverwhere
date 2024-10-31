import os
import subprocess
import shutil
def bash_run(cmd):
    COLMAP_BIN = os.getenv('COLMAP_BIN')
    cmd = COLMAP_BIN + ' ' + cmd
    print('\nRunning cmd: ', cmd)

    subprocess.check_call(['/bin/bash', '-c', cmd])

def run_sift_matching(img_dir, db_file, gpu_index, remove_exist=False):
    print('Running sift matching...')

    if remove_exist and os.path.exists(db_file):
        os.remove(db_file) # otherwise colmap will skip sift matching

    # feature extraction
    # if there's no attached display, cannot use feature extractor with GPU
    cmd = ' feature_extractor \
            --database_path {} \
            --image_path {} \
            --ImageReader.single_camera 1 \
            --ImageReader.camera_model SIMPLE_RADIAL \
            --SiftExtraction.max_image_size 5000  \
            --SiftExtraction.estimate_affine_shape 0 \
            --SiftExtraction.domain_size_pooling 1 \
            --SiftExtraction.use_gpu 1 \
            --SiftExtraction.max_num_features 16384 \
            --SiftExtraction.gpu_index {}'.format(db_file, img_dir, gpu_index)
    bash_run(cmd)

    # feature matching
    cmd = ' sequential_matcher \
            --database_path {} \
            --SiftMatching.guided_matching 1 \
            --SiftMatching.use_gpu 1 \
            --SiftMatching.max_num_matches 65536 \
            --SiftMatching.gpu_index {}'.format(db_file, gpu_index)

    bash_run(cmd)


def run_sfm(img_dir, db_file, sparse_dir):
    print('Running SfM...')

    cmd = ' mapper \
            --database_path {} \
            --image_path {} \
            --output_path {} \
            --Mapper.tri_min_angle 3.0 \
            --Mapper.filter_min_tri_angle 3.0'.format(db_file, img_dir, sparse_dir)
 
    bash_run(cmd)


def prepare_mvs(img_dir, sparse_dir, mvs_dir):
    print('Preparing for MVS...')

    cmd = ' image_undistorter \
            --image_path {} \
            --input_path {} \
            --output_path {} \
            --output_type COLMAP \
            --max_image_size 2000'.format(img_dir, sparse_dir, mvs_dir)

    bash_run(cmd)
    

def run_model_converter(input_dir, sparse_dir):
    print('Converting model to TXT format...')
    
    cmd = ' model_converter \
            --input_path {} \
            --output_path {} \
            --output_type TXT'.format(input_dir, sparse_dir)
    bash_run(cmd)


def main(img_dir, output_dir, gpu_index='-1'):
    """
    Run COLMAP SfM pipeline
    Args:
        img_dir: Directory containing input images
        output_dir: Directory for COLMAP output files
        gpu_index: GPU index to use for SIFT extraction and matching
    """
    # Check if required text files already exist
    sparse_dir = os.path.join(output_dir, 'sparse')
    required_files = [
        os.path.join(sparse_dir, 'cameras.txt'),
        os.path.join(sparse_dir, 'images.txt'),
        os.path.join(sparse_dir, 'points3D.txt')
    ]
    
    if all(os.path.exists(f) for f in required_files):
        print("\n=== COLMAP text files already exist, skipping COLMAP pipeline ===")
        return
    
    # Delete COLMAP folder if it exists but doesn't have required files
    if os.path.exists(output_dir) and not all(os.path.exists(f) for f in required_files):
        print("\n=== Incomplete COLMAP files found, removing COLMAP folder ===")
        shutil.rmtree(output_dir)
        
    print('Running COLMAP pipeline...')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Define database path
    db_file = os.path.join(output_dir, 'database.db')
    sparse_dir = os.path.join(output_dir, 'sparse')
    mvs_dir = os.path.join(output_dir, 'mvs')  # Add MVS directory
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(mvs_dir, exist_ok=True)  # Create MVS directory
    
    # Run SIFT matching
    run_sift_matching(img_dir, db_file, gpu_index, remove_exist=False)
    
    # Run SfM
    run_sfm(img_dir, db_file, sparse_dir)
    
    # Prepare for MVS (undistort images)
    prepare_mvs(img_dir, sparse_dir + '/0', mvs_dir)
    
    # Convert model to TXT format (now using MVS output)
    run_model_converter(mvs_dir + '/sparse', sparse_dir)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run COLMAP SfM pipeline')
    parser.add_argument('--img-dir', type=str, required=True,
                      help='Directory containing input images')
    parser.add_argument('--output-dir', type=str, required=True,
                      help='Directory for COLMAP output files')
    parser.add_argument('--gpu-index', type=str, default='-1',
                      help='GPU index to use for SIFT extraction and matching')
    
    args = parser.parse_args()
    
    # Run the COLMAP pipeline
    main(
        img_dir=args.img_dir,
        output_dir=args.output_dir,
        gpu_index=args.gpu_index
    )

