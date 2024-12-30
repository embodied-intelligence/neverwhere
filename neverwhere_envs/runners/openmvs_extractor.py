import numpy as np
import struct
import cv2
import argparse
from pathlib import Path

class HeaderDepthDataRaw:
    HAS_DEPTH = (1<<0)
    HAS_NORMAL = (1<<1)
    HAS_CONF = (1<<2)
    HAS_VIEWS = (1<<3)

def read_dmap(filename):
    with open(filename, 'rb') as f:
        # Read header
        name = struct.unpack('H', f.read(2))[0]  # uint16_t name
        type_padding = struct.unpack('BB', f.read(2))  # uint8_t type, padding
        type_flags = type_padding[0]
        
        # Read image and depth dimensions
        image_width, image_height = struct.unpack('II', f.read(8))
        depth_width, depth_height = struct.unpack('II', f.read(8))
        
        # Read depth range
        d_min, d_max = struct.unpack('ff', f.read(8))
        
        # Read filename length and filename
        filename_size = struct.unpack('H', f.read(2))[0]
        image_filename = f.read(filename_size).decode('utf-8')
        
        # Read number of view IDs and IDs
        num_ids = struct.unpack('I', f.read(4))[0]
        view_ids = struct.unpack(f'{num_ids}I', f.read(4 * num_ids))
        
        # Read camera matrices
        K = np.array(struct.unpack('9d', f.read(72))).reshape(3,3)  # 3x3 camera matrix
        R = np.array(struct.unpack('9d', f.read(72))).reshape(3,3)  # 3x3 rotation matrix
        C = np.array(struct.unpack('3d', f.read(24)))  # 3x1 position vector
        
        # Read depth map
        depth_map = None
        if type_flags & HeaderDepthDataRaw.HAS_DEPTH:
            depth_data = f.read(depth_width * depth_height * 4)  # float32 array
            depth_map = np.frombuffer(depth_data, dtype=np.float32).reshape(depth_height, depth_width)
            
        # Read normal map if present
        normal_map = None
        if type_flags & HeaderDepthDataRaw.HAS_NORMAL:
            normal_data = f.read(depth_width * depth_height * 12)  # float32 array x 3
            normal_map = np.frombuffer(normal_data, dtype=np.float32).reshape(depth_height, depth_width, 3)
            
        # Read confidence map if present
        confidence_map = None
        if type_flags & HeaderDepthDataRaw.HAS_CONF:
            conf_data = f.read(depth_width * depth_height * 4)  # float32 array
            confidence_map = np.frombuffer(conf_data, dtype=np.float32).reshape(depth_height, depth_width)
            
        # Read views map if present
        views_map = None
        if type_flags & HeaderDepthDataRaw.HAS_VIEWS:
            views_data = f.read(depth_width * depth_height * 4)  # uint32 array
            views_map = np.frombuffer(views_data, dtype=np.uint32).reshape(depth_height, depth_width)
            
        return {
            'image_size': (image_width, image_height),
            'depth_size': (depth_width, depth_height),
            'depth_range': (d_min, d_max),
            'image_filename': image_filename,
            'view_ids': view_ids,
            'K': K,
            'R': R,
            'C': C,
            'depth_map': depth_map,
            'normal_map': normal_map,
            'confidence_map': confidence_map,
            'views_map': views_map
        }

def main(scene_dir: str, verbose: bool = False, keys=None):
    """Process depth maps from OpenMVS output and save them in geo2d directory.
    
    Args:
        scene_dir: Path to the scene directory
        verbose: If True, save visualization images along with numpy arrays
        keys: List of keys to process. Valid keys are 'depth', 'confidence', 'normal', 'views'.
             If None, defaults to ['depth', 'confidence']
    """
    if keys is None:
        keys = ['depth', 'confidence']
    
    scene_path = Path(scene_dir)
    openmvs_dir = scene_path / "openmvs"
    geo2d_dir = scene_path / "geo2d"
    
    # Create output directories based on requested keys
    output_dirs = {}
    for key in keys:
        dir_path = geo2d_dir / key
        dir_path.mkdir(parents=True, exist_ok=True)
        output_dirs[key] = dir_path
    
    # Find all dmap files
    dmap_files = list(openmvs_dir.glob("**/*.dmap"))
    if not dmap_files:
        print(f"No .dmap files found in {openmvs_dir}")
        return
    
    # Check which keys need processing
    keys_to_process = []
    for key in keys:
        output_dir = output_dirs[key]
        existing_files = list(output_dir.glob("*.npy"))
        if len(existing_files) != len(dmap_files):
            keys_to_process.append(key)
        else:
            print(f"Skipping {key} - already processed ({len(dmap_files)} files exist)")
    
    if not keys_to_process:
        print("All data already extracted. Skipping extraction.")
        return
        
    print(f"Processing {len(dmap_files)} depth maps for keys: {keys_to_process}")
    
    for dmap_file in dmap_files:
        try:
            data = read_dmap(str(dmap_file))
            base_name = Path(data['image_filename']).stem
            
            # Process each requested key
            for key in keys_to_process:
                map_key = f'{key}_map'
                if map_key not in data or data[map_key] is None:
                    continue
                
                # Save numpy array
                output_path = output_dirs[key] / f"{base_name}.npy"
                np.save(str(output_path), data[map_key])
                
                if verbose:
                    # Create visualization
                    if key in ['depth', 'confidence']:
                        # For scalar maps
                        data_min = data[map_key].min()
                        data_max = data[map_key].max()
                        viz = ((data[map_key] - data_min) / (data_max - data_min) * 255).astype(np.uint8)
                    elif key == 'normal':
                        # For normal maps, convert from [-1,1] to [0,255]
                        viz = ((data[map_key] + 1) * 127.5).astype(np.uint8)
                    else:  # views
                        # For views map, just normalize to [0,255]
                        viz = cv2.normalize(data[map_key], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                    
                    cv2.imwrite(str(output_dirs[key] / f"{base_name}.png"), viz)
                    
        except Exception as e:
            print(f"Error processing {dmap_file}: {e}")
    
    for key, dir_path in output_dirs.items():
        print(f"Processed {key} maps saved to {dir_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process OpenMVS depth maps')
    parser.add_argument('--scene-dir', type=str, required=True,
                      help='Path to the scene directory')
    parser.add_argument('--verbose', action='store_true',
                      help='Save visualization images along with numpy arrays')
    parser.add_argument('--keys', nargs='+', default=['depth', 'confidence'],
                      choices=['depth', 'confidence', 'normal', 'views'],
                      help='Types of data to process')
    
    args = parser.parse_args()
    main(args.scene_dir, args.verbose, args.keys)
