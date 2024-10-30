import argparse
from pathlib import Path
from neverwhere_envs.runners.sort_images import main as downsample_main
from neverwhere_envs.runners.colmap_runner import main as colmap_main
from neverwhere_envs.runners.openmvs_runner import main as openmvs_main
from neverwhere_envs.runners.geometry_processor import process_scene as geometry_main

def main():
    parser = argparse.ArgumentParser(description="Launch Neverwhere reconstruction pipeline")
    parser.add_argument("--scene-name", required=True, help="Name of the scene to process, or 'all' to process all scenes")
    parser.add_argument("--dataset-dir", required=True, help="Path to the datasets directory")
    parser.add_argument("--gpu-index", type=str, default='-1', help="GPU index to use for COLMAP and OpenMVS processing")
    parser.add_argument("--downsample", type=int, default=2, help="Downsampling factor (default: 2)")
    parser.add_argument("--downsample-threshold", type=int, default=200, 
                       help="Minimum number of images required for downsampling (default: 200)")
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
    
def process_scene(scene_name: str, dataset_dir: Path, args):
    # Setup directories
    scene_dir = dataset_dir / scene_name
    colmap_path = scene_dir / "colmap"
    openmvs_dir = scene_dir / "openmvs"
    images_dir = scene_dir / "images"
    
    # Create necessary directories
    colmap_path.mkdir(parents=True, exist_ok=True)
    openmvs_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Process images
    print("\n=== Processing images ===")
    downsample_main(
        input_dir=str(scene_dir), 
        downsample=args.downsample,
        downsample_threshold=args.downsample_threshold,
    )
    
    # Step 2: Run COLMAP pipeline
    print("\n=== Running COLMAP pipeline ===")
    colmap_main(
        img_dir=str(scene_dir / "images"),
        output_dir=str(colmap_path),
        gpu_index=args.gpu_index
    )

    # Step 3: Run OpenMVS pipeline
    print("\n=== Running OpenMVS pipeline ===")
    openmvs_main(
        working_dir=str(openmvs_dir),
        colmap_dir=str(colmap_path),
        image_dir=str(scene_dir / "images"),
        gpu_index=args.gpu_index
    )
    
    # Step 4: Process geometry
    print("\n=== Processing geometry ===")
    geometry_main(str(scene_dir))
    
    # Step 5: Train 3DGS
    # [WIP]
    

if __name__ == "__main__":
    main() 