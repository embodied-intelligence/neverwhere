import os
import subprocess
import shutil
def bash_run(cmd):
    COLMAP_BIN = os.getenv('COLMAP_BIN')
    cmd = COLMAP_BIN + ' ' + cmd
    print('\nRunning cmd: ', cmd)

    subprocess.check_call(['/bin/bash', '-c', cmd])

def run_sift_matching_sequential(img_dir, db_file, gpu_index, remove_exist=False):
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
            --SiftExtraction.estimate_affine_shape 0 \
            --SiftExtraction.use_gpu 1 \
            --SiftExtraction.gpu_index {}'.format(db_file, img_dir, gpu_index)
    bash_run(cmd)

    # feature matching
    cmd = ' sequential_matcher \
            --database_path {} \
            --SiftMatching.guided_matching 1 \
            --SiftMatching.use_gpu 1 \
            --SiftMatching.gpu_index {}'.format(db_file, gpu_index)

    bash_run(cmd)
    
def run_sift_matching_exhaustive(img_dir, db_file, gpu_index, remove_exist=False):
    print('Running sift matching with exhaustive matcher...')

    if remove_exist and os.path.exists(db_file):
        os.remove(db_file) # otherwise colmap will skip sift matching

    # feature extraction
    cmd = ' feature_extractor \
            --database_path {} \
            --image_path {} \
            --ImageReader.single_camera 1 \
            --ImageReader.camera_model SIMPLE_RADIAL \
            --SiftExtraction.estimate_affine_shape 0 \
            --SiftExtraction.use_gpu 1 \
            --SiftExtraction.gpu_index {}'.format(db_file, img_dir, gpu_index)
    bash_run(cmd)

    # feature matching
    cmd = ' exhaustive_matcher \
            --database_path {} \
            --SiftMatching.guided_matching 1 \
            --SiftMatching.use_gpu 1 \
            --SiftMatching.gpu_index {}'.format(db_file, gpu_index)
    bash_run(cmd)

def run_sfm(img_dir, db_file, sparse_dir):
    print('Running SfM...')

    cmd = ' mapper \
            --database_path {} \
            --image_path {} \
            --output_path {}'.format(db_file, img_dir, sparse_dir)
 
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

def check_matching_results(log_dir, img_dir):
    """Check the percentage of valid images after matching"""
    images_txt = os.path.join(log_dir, 'images.txt')
    if not os.path.exists(images_txt):
        raise FileNotFoundError(f"images.txt not found in {log_dir}")
        
    valid_images = 0
    total_images = len([f for f in os.listdir(img_dir) 
                       if f.endswith(('.jpg', '.png'))])
    
    with open(images_txt, 'r') as f:
        is_camera_description_line = False
        for line in iter(lambda: f.readline().strip(), ''):
            if not line or line.startswith('#'):
                continue
            is_camera_description_line = not is_camera_description_line
            if is_camera_description_line:
                valid_images += 1
    
    return (valid_images / total_images) * 100 if total_images > 0 else 0.0

def main(img_dir, output_dir, gpu_index='-1'):
    """Run COLMAP SfM pipeline with fallback to vocab_tree if sequential fails"""
    print('Running COLMAP pipeline...')
    
    os.makedirs(output_dir, exist_ok=True)
    db_file = os.path.join(output_dir, 'database.db')
    sparse_dir = os.path.join(output_dir, 'sparse')
    mvs_dir = os.path.join(output_dir, 'mvs')
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(mvs_dir, exist_ok=True)

    # Check if required text files already exist
    required_files = [
        os.path.join(sparse_dir, 'cameras.txt'),
        os.path.join(sparse_dir, 'images.txt'),
        os.path.join(sparse_dir, 'points3D.txt')
    ]
    
    if all(os.path.exists(f) for f in required_files):
        print("\n=== COLMAP text files already exist, skipping COLMAP pipeline ===")
        return True

    # Try sequential matching first
    print("\nAttempting sequential matching...")
    run_sift_matching_sequential(img_dir, db_file, gpu_index, remove_exist=False)
    run_sfm(img_dir, db_file, sparse_dir)
    run_model_converter(sparse_dir + '/0', sparse_dir)
    valid_percentage = check_matching_results(sparse_dir, img_dir)
    
    # If sequential fails, try exhaustive matching
    if valid_percentage < 50:
        print(f"\nSequential matching resulted in only {valid_percentage:.1f}% valid images")
        print("Attempting exhaustive matching...")
        
        # Clean up previous attempt
        shutil.rmtree(sparse_dir)
        os.makedirs(sparse_dir, exist_ok=True)
        if os.path.exists(db_file):
            os.remove(db_file)
        
        # Try exhaustive matching
        run_sift_matching_exhaustive(img_dir, db_file, gpu_index, remove_exist=True)
        run_sfm(img_dir, db_file, sparse_dir)
        run_model_converter(sparse_dir + '/0', sparse_dir)
        valid_percentage = check_matching_results(sparse_dir, img_dir)
        
    if valid_percentage >= 50:
        # Proceed with MVS preparation only if we have good results
        prepare_mvs(img_dir, sparse_dir + '/0', mvs_dir)
        # remove all txt files in sparse_dir
        for file in os.listdir(sparse_dir):
            if file.endswith('.txt'):
                os.remove(os.path.join(sparse_dir, file))
        # convert mvs sparse to txt
        run_model_converter(mvs_dir + '/sparse', sparse_dir)
        return True
    else:
        print(f"\nBoth matching methods failed. Final valid percentage: {valid_percentage:.1f}%")
        return False

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

