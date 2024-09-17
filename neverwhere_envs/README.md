# Neverwhere Envs

## Available Scenes

<details>
<summary>Environments with Polycam Scans</summary>

1. building_31_stairs_v1
2. curb_gas_tank_v1
3. gaps_12in_226_blue_carpet_v2
4. gaps_16in_226_blue_carpet_v2
5. gaps_226_blue_carpet_v4
6. gaps_fire_outlet_v3
7. gaps_grassy_courtyard_v2
8. gaps_stata_v1
9. hurdle_226_blue_carpet_v3
10. hurdle_black_stone_v1
11. hurdle_one_blue_carpet_v2
12. hurdle_one_dark_grassy_courtyard_v1
13. hurdle_one_light_grassy_courtyard_v1
14. hurdle_one_light_grassy_courtyard_v3
15. hurdle_stata_one_v1
16. hurdle_stata_v1
17. hurdle_stata_v2
18. hurdle_three_grassy_courtyard_v2
19. ramp_aligned_blue_carpet_v4
20. ramp_aligned_covered_blue_carpet_v6
21. ramp_bricks_v2
22. ramp_grass_v1
23. ramp_grass_v3
24. ramp_spread_blue_carpet_v5
25. ramp_spread_covered_blue_carpet_v7
26. real_hurdle_one_blue_carpet_v2
27. real_hurdle_three_grassy_ally_v2
28. real_stair_02_bcs_v1
29. real_stair_03_bcs_golden
30. real_stair_04_bcs_dusk
31. real_stair_07_54_v1
32. real_stair_08_mc_afternoon_v1
33. stairs_36_backstairs_v2
34. stairs_48_v3
35. stairs_4_stairs2up_v1
36. stairs_54_wooden_v1
37. stairs_backstairs_v5
38. stairs_banana_v1
39. stata_ramped_platform_v3
40. wood_ramp_aligned_bricks_v1
41. wood_ramp_aligned_grass_v2
42. wood_ramp_offset_bricks_v2
43. wood_ramp_offset_grass_v1

</details>

<details>
<summary>Environments without Polycam Scans</summary>

1. _archive
2. gap-stata_v1
3. mesh_camera_left
4. mesh_camera_right
5. real_curb_01
6. real_curb_02
7. real_flat_01_stata_grass
8. real_flat_02_wh_evening
9. real_flat_03_stata_indoor
10. real_gap_01
11. real_gap_02
12. real_hurdle_01
13. real_parkour_01
14. real_stair_01
15. real_stair_05_bcs_rain_v1
16. real_stair_06_wh_evening_v1
17. real_stair_10_wh_afternoon_v1
18. stairs_cf_night_v13
19. stairs_mc_afternoon_v2
20. stairs_wh_evening_v2

</details>

## File Structure [Current]

Each environment typically follows this file structure:

```
pathtoenvs/
    ├── scene000_name/
    │   ├── environment_name.xml
    │   ├── meshes/
    │   ├── model.ckpt
    │   ├── polycam/
    │   └── transforms/
    ├── scene001_name/
    │   ├── environment_name.xml
    │   ├── meshes/
    │   ├── model.ckpt
    │   ├── polycam/
    │   └── transforms/
    └── ...
```

#### Description of files and directories:

1. `environment_name.xml`: XML file containing environment configuration.
2. `meshes/`: Directory containing mesh files and `.spalt` for the environment.
3. `model.ckpt`: 3DGS Checkpoint file.
4. `polycam/`: Directory containing Polycam raw data (may be absent in some environments).
5. `transforms/`: Directory containing `gsplat<->mesh` transformation data

Note: Some environments may have variations in this structure, particularly those listed as not having Polycam scans.

## File Structure [Desired]

```
polycam/           # contains the raw polycam data
mesh_openmvs/      # openmvs reconstructed meshes
    colmap/
    polycam/
nerfstudio_data/   
    colmap/
    polycam/
gsplat/
    model.ckpt
    splat.ply.splat
    splat.ply (optional)
```

#### Minimal Structure (choose the better one from colmap and polycam):
```
polycam/           # contains the raw polycam data
mesh_openmvs/      # openmvs reconstructed meshes (choose the better one from colmap and polycam)
nerfstudio_data/   # choose the better one from colmap and polycam
gsplat/
    model.ckpt
    splat.ply.splat
```

## Create Your Own Data

Follow these simple steps to add a new environment to the Neverwhere project:

### Step 1: Obtaining Polycam Scans

1. Use the Polycam app to capture a 3D scan of your desired environment.
2. Export the raw data from Polycam.

### Step 2: Setting Up the Environment Structure

1. Create a new directory for your environment under `projectpage/neverwhere_envs/datasets`:
   ```
   mkdir projectpage/neverwhere_envs/datasets/your_environment_name
   ```

2. Place the Polycam raw data in a `polycam` folder within your new environment directory:
   ```
   mkdir projectpage/neverwhere_envs/datasets/your_environment_name/polycam
   ```
   Copy your Polycam raw data into this `polycam` folder.

3. Your new environment structure should look like this:
   ```
   projectpage/neverwhere_envs/datasets/
   └── your_environment_name/
       └── polycam/
           └── [Polycam raw data files]
   ```

### Step 3: Setting Up NeRFStudio Environment

We use [nerfstudio](https://github.com/nerfstudio-project/nerfstudio) to generate COLMAP poses (Polycam data alone may not provide sufficient accuracy.) and point clouds.

1. Install nerfstudio: [Installation Guide](https://docs.nerf.studio/quickstart/installation.html#create-environment)
2. Install COLMAP in nerfstudio: [COLMAP Setup](https://docs.nerf.studio/quickstart/custom_dataset.html#installing-colmap)

### Step 4: Setting Up OpenMVS Environment

We use [OpenMVS](https://github.com/cdcseacave/openMVS) to generate high-quality meshes for:
- Initializing 3D Gaussians for high-quality 3DGS Reconstruction
- Creating accurate collision geometry for the environment

Follow the installation instructions in the [OpenMVS Building Guide](https://github.com/cdcseacave/openMVS/wiki/Building).

<details>
<summary>Click here for a modified installation guide</summary>

#### Prepare and empty machine for building:
```bash
sudo apt-get update -qq && sudo apt-get install -qq
sudo apt-get -y install git cmake libpng-dev libjpeg-dev libtiff-dev libglu1-mesa-dev
main_path=$(pwd)
```

#### Eigen (Required)
```bash
git clone https://gitlab.com/libeigen/eigen.git --branch 3.4
mkdir eigen_build && cd eigen_build
cmake ../eigen
make && sudo make install
cd ..
```

#### Boost (Required)
```bash
sudo apt-get -y install libboost-iostreams-dev libboost-program-options-dev libboost-system-dev libboost-serialization-dev
```

#### OpenCV (Required)
```bash
sudo apt-get -y install libopencv-dev
```

#### CGAL (Required)
```bash
sudo apt-get -y install libcgal-dev libcgal-qt5-dev
```

#### VCGLib (Required)
```bash
git clone https://github.com/cdcseacave/VCG.git vcglib
```

#### Ceres (Optional)
```bash
sudo apt-get -y install libatlas-base-dev libsuitesparse-dev
git clone https://ceres-solver.googlesource.com/ceres-solver ceres-solver
mkdir ceres_build && cd ceres_build
cmake ../ceres-solver/ -DMINIGLOG=ON -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF
make -j2 && sudo make install
cd ..
```

#### GLFW3 (Optional)
```bash
sudo apt-get -y install freeglut3-dev libglew-dev libglfw3-dev
```

#### OpenMVS
```bash
git clone https://github.com/cdcseacave/openMVS.git
mkdir make && cd make
cmake .. -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="$main_path/vcglib"
```

#### Install OpenMVS library (optional):
```bash
make -j4 && sudo make install
```

</details>

### Step 5: Extracting Poses and Process Data

Run the following commands to set up your environment:

```bash
conda activate nerfstudio
export PYTHONPATH=$(pwd) # the path to neverwhere project root
```

**Ziyu: we need to find a better one and only use the better one in the final version** 
#### Option 1: Colmap Process

1. Extract pose:
    ```bash
    SCENE_NAME=your_scene_name
    DATASET_DIR=$PYTHONPATH/neverwhere_envs/datasets
    SCENE_DIR=$DATASET_DIR/$SCENE_NAME
    IMAGES_PATH=$SCENE_DIR/polycam/keyframes/correct_images
    if [ ! -d "$IMAGES_PATH" ]; then
        IMAGES_PATH=$SCENE_DIR/polycam/keyframes/images
    fi
    OUTPUT_PATH=$SCENE_DIR/nerfstudio_data/colmap

    ns-process-data images --data $IMAGES_PATH --output-dir $OUTPUT_PATH --matching-method exhaustive --num_downscales 0 --camera_type pinhole
    ```

    This script will first look for a `correct_images` folder. If it doesn't exist, it will use the `images` folder instead.

2. Prepare colmap data for OpenMVS
    ```bash
    colmap model_converter --input_path $OUTPUT_PATH/colmap/sparse/0 --output_path $OUTPUT_PATH/colmap/sparse --output_type TXT
    ```

3. Run OpenMVS to get textured Mesh
    ```bash
    MESH_DIR=$SCENE_DIR/mesh_openmvs

    # Interface COLMAP
    InterfaceCOLMAP -w $MESH_DIR -i $OUTPUT_PATH/colmap/ -o $MESH_DIR/model_colmap.mvs

    ln -s $OUTPUT_PATH/images $MESH_DIR/images

    # Densify Point Cloud
    DensifyPointCloud -i $MESH_DIR/model_colmap.mvs \
        -o $MESH_DIR/model_dense.mvs \
        -w $MESH_DIR \
        -v 1

    # Reconstruct Mesh
    ReconstructMesh -i $MESH_DIR/model_dense.mvs \
        -p $MESH_DIR/model_dense.ply \
        -o $MESH_DIR/model_dense_recon.mvs \
        -w $MESH_DIR

    # Refine Mesh
    RefineMesh -i $MESH_DIR/model_dense.mvs \
        -m $MESH_DIR/model_dense_recon.ply \
        -o $MESH_DIR/model_dense_mesh_refine.mvs \
        -w $MESH_DIR \
        --scales 1 \
        --max-face-area 16

    # Texture Mesh
    TextureMesh $MESH_DIR/model_dense.mvs \
        -m $MESH_DIR/model_dense_mesh_refine.ply \
        -o $MESH_DIR/model_dense_mesh_refine_texture.mvs \
        -w $MESH_DIR
    ```

4. Extract Mesh's Vertices for Gaussian Initialization
   This step renames the point cloud file created by COLMAP and generates a new point cloud file for Nerfstudio input.
   ```bash
   mv $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply $SCENE_DIR/nerfstudio_data/colmap/colmap_pc.ply
   python neverwhere_envs/extract_gsplat_init.py \
       -i $MESH_DIR/model_dense_mesh_refine_texture.ply \
       -t $MESH_DIR/model_dense_mesh_refine_texture0.png \
       -o $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply
   ```

5. Run NerfStudio's SplatFacto to get the trained 3DGS
   ```bash
   ns-train splatfacto-big --data $SCENE_DIR/nerfstudio_data/colmap/transforms.json \
       --output-dir $SCENE_DIR/gsplat \
       --pipeline.model.cull_alpha_thresh=0.05 \
       --pipeline.model.densify_grad_thresh=0.0008 \
       --pipeline.model.stop_split_at=30000 \
       --pipeline.model.max_gauss_ratio=5.0 \
       --pipeline.model.use_scale_regularization=True
   ```
   Note: We do not use scene pose auto-scale or auto-orientation to maintain alignment with OpenMVS. This eliminates the need for subsequent mesh alignment with the 3DGS model.


#### Option 2: Polycam Process

1. Extract pose
    ```bash
    SCENE_NAME=your_scene_name
    DATASET_DIR=$PYTHONPATH/neverwhere_envs/datasets
    SCENE_DIR=$DATASET_DIR/$SCENE_NAME
    IMAGES_PATH=$SCENE_DIR/polycam
    OUTPUT_PATH=$SCENE_DIR/nerfstudio_data/polycam

    ns-process-data polycam --data $IMAGES_PATH --output-dir $OUTPUT_PATH --num_downscales 0
    ```
**[WIP]**