import argparse
import shutil
from pathlib import Path
from neverwhere_envs.runners.sort_images import main as downsample_main
from neverwhere_envs.runners.colmap_runner import main as colmap_main
from neverwhere_envs.runners.openmvs_runner import main as openmvs_main
from neverwhere_envs.runners.geometry_processor import process_scene as geometry_main
from neverwhere_envs.runners.gsplat_runner import main as gsplat_main
from neverwhere_envs.runners.gsplat2d_runner import main as gsplat2d_main

def check_colmap(scene_dir, colmap_path):
    # Count total images in images directory
    images_dir = scene_dir / "images"
    total_images = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
    
    # Count valid images from COLMAP
    images_txt = colmap_path / "sparse" / "images.txt"
    valid_images = 0
    
    with open(images_txt, 'r') as f:
        is_camera_description_line = False
        for line in iter(lambda: f.readline().strip(), ''):
            if not line or line.startswith('#'):
                continue
            is_camera_description_line = not is_camera_description_line
            if is_camera_description_line:
                valid_images += 1
                
    # Calculate percentage
    valid_percentage = (valid_images / total_images) * 100
    print(f"\nCOLMAP validation check:")
    print(f"Total images: {total_images}")
    print(f"Valid images: {valid_images}")
    print(f"Valid percentage: {valid_percentage:.1f}%")
    
    # Check if valid images are less than 50%
    if valid_percentage < 50:
        print("\nWARNING: Less than 50% of images were successfully processed by COLMAP")
        
        # Create error log
        error_log = scene_dir / "error.log"
        with open(error_log, 'w') as f:
            f.write(f"COLMAP Processing Failed\n")
            f.write(f"Total images: {total_images}\n")
            f.write(f"Successfully processed: {valid_images}\n")
            f.write(f"Success rate: {valid_percentage:.1f}%\n")
        
        return False
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Launch Neverwhere reconstruction pipeline")
    parser.add_argument("--scene-name", required=True, help="Name of the scene to process, or 'all' to process all scenes")
    parser.add_argument("--dataset-dir", required=True, help="Path to the datasets directory")
    parser.add_argument("--gpu-index", type=str, default='-1', help="GPU index to use for COLMAP and OpenMVS processing")
    parser.add_argument("--downsample", type=int, default=2, help="Downsampling factor (default: 2)")
    parser.add_argument("--downsample-threshold", type=int, default=200, 
                       help="Minimum number of images required for downsampling (default: 200)")
    parser.add_argument("--gs-type", type=str, choices=['3dgs', '2dgs', '2dgs+3dgs'], default='3dgs',
                       help="Type of Gaussian Splatting to use (default: 3dgs)")
    parser.add_argument("--skip-gs", action="store_true", help="Skip Gaussian Splatting training")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_dir)
    
    if args.scene_name == 'all':
        # Process all subdirectories in dataset_dir
        scene_dirs = [d for d in sorted(dataset_path.iterdir()) if d.is_dir()]
        for scene_dir in scene_dirs:
            try:
                print(f"\n==================== Processing scene: {scene_dir.name} ====================")
                process_scene(scene_dir.name, dataset_path, args)
            except Exception as e:
                print(f"Error processing scene {scene_dir.name}: {e}")
    else:
        process_scene(args.scene_name, dataset_path, args)
    
def run_3dgs_training(scene_dir, gsplat_3d_dir, gpu_index, strategy="default"):
    from gsplat.strategy import DefaultStrategy, MCMCStrategy
    print("\n=== Training 3DGS ===")
    
    if strategy == "default":
        gsplat_main(
            data_dir=str(scene_dir),
            result_dir=str(gsplat_3d_dir),
            gpu_index=gpu_index,
            init_type="openmvs",
            random_bkgd=True,
            disable_viewer=True,
            pose_opt=True,
            strategy=DefaultStrategy(verbose=True),
        )
    elif strategy == "mcmc":
        gsplat_main(
            data_dir=str(scene_dir),
            result_dir=str(gsplat_3d_dir),
            gpu_index=gpu_index,
            init_type="openmvs",
            random_bkgd=True,
            disable_viewer=True,
            pose_opt=True,
            strategy=MCMCStrategy(verbose=True),
            init_opa=0.5,
            init_scale=0.1,
            opacity_reg=0.01,
            scale_reg=0.01,
        )
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

def run_2dgs_training(scene_dir, gsplat_2d_dir, gpu_index):
    print("\n=== Training 2DGS ===")
    gsplat2d_main(
        data_dir=str(scene_dir),
        result_dir=str(gsplat_2d_dir),
        gpu_index=gpu_index,
        init_type="openmvs",
        random_bkgd=True,
        disable_viewer=True,
        pose_opt=True,
        normal_loss=True,
        dist_loss=True,
        # absgrad=True,
        # grow_grad2d=0.0006,
    )

def process_scene(scene_name: str, dataset_dir: Path, args):
    # Setup directories
    scene_dir = dataset_dir / scene_name
    colmap_path = scene_dir / "colmap"
    openmvs_dir = scene_dir / "openmvs"
    gsplat_3d_dir = scene_dir / "3dgs"
    gsplat_2d_dir = scene_dir / "2dgs"
    images_dir = scene_dir / "images"
    
    # Step 1: Process images
    print("\n=== Processing images ===")
    delete_cache = downsample_main(
        input_dir=str(scene_dir), 
        downsample=args.downsample,
        downsample_threshold=args.downsample_threshold,
    )
    
    if delete_cache:
        for folder in ["colmap", "openmvs", "geometry", "3dgs", "2dgs"]:
            folder_path = scene_dir / folder
            if folder_path.exists():
                shutil.rmtree(folder_path)
    
    # Step 2: Run COLMAP pipeline
    print("\n=== Running COLMAP pipeline ===")
    colmap_main(
        img_dir=str(images_dir),
        output_dir=str(colmap_path),
        gpu_index=args.gpu_index
    )
            
    # Run COLMAP validation check
    if not check_colmap(scene_dir, colmap_path):
        print("Scene processing stopped due to failure of COLMAP")
        for folder in ["openmvs", "geometry", "3dgs", "2dgs"]:
            folder_path = scene_dir / folder
            if folder_path.exists():
                shutil.rmtree(folder_path)
        return

    # Step 3: Run OpenMVS pipeline
    print("\n=== Running OpenMVS pipeline ===")
    openmvs_main(
        working_dir=str(openmvs_dir),
        colmap_dir=str(colmap_path),
        image_dir=str(images_dir),
        gpu_index=args.gpu_index
    )
    
    # Step 4: Process geometry
    print("\n=== Processing geometry ===")
    geometry_main(str(scene_dir))
    
    # Step 5: Train Gaussian Splatting
    if not args.skip_gs:
        if args.gs_type == '2dgs+3dgs':
            run_3dgs_training(scene_dir, gsplat_3d_dir, args.gpu_index)
            run_2dgs_training(scene_dir, gsplat_2d_dir, args.gpu_index)
        elif args.gs_type == '3dgs':
            run_3dgs_training(scene_dir, gsplat_3d_dir, args.gpu_index)
        else:  # 2dgs
            run_2dgs_training(scene_dir, gsplat_2d_dir, args.gpu_index)
    

if __name__ == "__main__":
    main() 