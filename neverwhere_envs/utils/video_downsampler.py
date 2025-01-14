import cv2
import os
from pathlib import Path

def count_frames(video_path):
    """Count total frames in a video file"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames

def downsample_video(video_path, output_dir, target_frames):
    """
    Downsample a video by extracting frames to reach target frame count.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save output frames
        target_frames: Desired number of output frames
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open video file
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    downsample_factor = max(1, total_frames // target_frames)

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
            
        # Save every nth frame
        if frame_count % downsample_factor == 0:
            # Use actual frame index in filename
            frame_path = output_dir / f"frame_{frame_count:06d}.png"
            cv2.imwrite(str(frame_path), frame)
            saved_count += 1
            
        frame_count += 1

    cap.release()
    print(f"Saved {saved_count} frames from {frame_count} total frames")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Downsample video to frames")
    parser.add_argument("--video_path", type=str, help="Path to input video file")
    parser.add_argument("--output_dir", type=str, help="Directory to save output frames")
    
    args = parser.parse_args()
    
    total_frames = count_frames(args.video_path)
    print(f"Video has {total_frames} total frames")
    target_frames = int(input("How many frames would you like to extract? "))
    
    downsample_video(args.video_path, args.output_dir, target_frames)
