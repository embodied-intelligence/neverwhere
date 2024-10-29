import argparse
from pathlib import Path
from neverwhere_envs.runners.sort_images import main as downsample_main
from neverwhere_envs.runners.colmap_runner import main as colmap_main
from neverwhere_envs.runners.openmvs_runner import main as openmvs_main

def main():
    parser = argparse.ArgumentParser(description="Launch Neverwhere reconstruction pipeline")
    parser.add_argument("--scene-name", required=True, help="Name of the scene to process, or 'all' to process all scenes")
    parser.add_argument("--dataset-dir", required=True, help="Path to the datasets directory")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_dir)
    
    if args.scene_name == 'all':
        # Process all subdirectories in dataset_dir
        scene_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
        for scene_dir in scene_dirs:
            print(f"\n=== Processing scene: {scene_dir.name} ===")
            process_scene(scene_dir.name, dataset_path)
    else:
        process_scene(args.scene_name, dataset_path)

def process_scene(scene_name: str, dataset_dir: Path):
    # Setup directories
    scene_dir = dataset_dir / scene_name
    colmap_path = scene_dir / "colmap"
    openmvs_dir = scene_dir / "openmvs"
    
    # Create necessary directories
    colmap_path.mkdir(parents=True, exist_ok=True)
    openmvs_dir.mkdir(parents=True, exist_ok=True)

    # Step 0: Downsample images
    print("\n=== Downsampling images ===")
    downsample_main(input_dir=str(scene_dir), downsample_factor=2)

    # Step 1: Run COLMAP pipeline
    print("\n=== Running COLMAP pipeline ===")
    colmap_main(
        img_dir=str(scene_dir / "images"),
        output_dir=str(colmap_path)
    )

    # Step 2: Run OpenMVS pipeline
    print("\n=== Running OpenMVS pipeline ===")
    openmvs_main(
        working_dir=str(openmvs_dir),
        colmap_dir=str(colmap_path),
        image_dir=str(scene_dir / "images")
    )

if __name__ == "__main__":
    main() 