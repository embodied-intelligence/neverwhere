import os
import argparse
import shutil
from pathlib import Path

def sample_and_rename_images(source_dir, dest_dir, downsample):
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    # Get all image files from the source directory
    image_files = sorted([f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    # Sample images at the specified interval
    sampled_images = image_files[::downsample]
    
    # Copy and rename sampled images
    for i, img in enumerate(sampled_images):
        src_path = os.path.join(source_dir, img)
        dest_path = os.path.join(dest_dir, f"{i:04d}{os.path.splitext(img)[1]}")
        shutil.copy2(src_path, dest_path)
    
    print(f"Sampled and renamed {len(sampled_images)} images to {dest_dir}")

def main(input_dir, downsample):
    scene_dir = Path(input_dir)
    polycam_dir = scene_dir / "polycam"
    
    if not polycam_dir.is_dir():
        print(f"Error: No 'polycam' directory found in {scene_dir}")
        return

    keyframes_dir = polycam_dir / "keyframes"
    corrected_images_dir = keyframes_dir / "corrected_images"
    images_dir = keyframes_dir / "images"

    if corrected_images_dir.is_dir():
        source_dir = corrected_images_dir
    elif images_dir.is_dir():
        source_dir = images_dir
    else:
        print(f"Error: Neither 'corrected_images' nor 'images' directory found in {keyframes_dir}")
        return

    raw_images_dir = scene_dir / "images"
    
    sample_and_rename_images(source_dir, raw_images_dir, downsample)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample and rename images from Polycam scene directory.")
    parser.add_argument("-i", "--input-dir", required=True, help="Path to the scene directory")
    parser.add_argument("-d", "--downsample", type=int, default=1, help="Downsampling factor (default: 1)")
    args = parser.parse_args()
    
    main(
        input_dir=args.input_dir,
        downsample=args.downsample,
    )