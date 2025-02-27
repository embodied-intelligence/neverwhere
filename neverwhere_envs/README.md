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
openmvs_outputs/      # openmvs reconstructed meshes
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
openmvs_outputs/      # openmvs reconstructed meshes (choose the better one from colmap and polycam)
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

### Step 3: Setting Up COLMAP Environment

We use [COLMAP](https://github.com/colmap/colmap) to generate camera poses and point clouds.

<details>
<summary>COLMAP Installation Guide</summary>

```bash
# Install dependencies
sudo apt-get update -qq && sudo apt-get install -qq
sudo apt-get install \
    git \
    cmake \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libcgal-qt5-dev

# Clone COLMAP
git clone https://github.com/colmap/colmap.git

# Build COLMAP
cd colmap
mkdir build
cd build
cmake ..
make -j
sudo make install
```
</details>

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

#### Python (Required)
```bash
sudo apt-get install -y python3-dev python3-pip python3.10-dev
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
cd openMVS
git checkout develop
mkdir make && cd make
cmake .. -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="$main_path/vcglib"
```

#### Install OpenMVS library:
```bash
make -j4
sudo make install
```

</details>

### Step 5: Extracting Poses and Process Data

Run the following commands to set up your environment:

```bash
conda activate nerfstudio
export PYTHONPATH=$(pwd) # the path to neverwhere project root
```

**Ziyu: we need to find a better one and only use the better one in the final version** 
#### Option 1: COLMAP Process

0. Set up environment and downsample images:
    ```bash
    # Set up environment
    SCENE_NAME=your_scene_name
    DATASET_DIR=$PYTHONPATH/neverwhere_envs/datasets
    SCENE_DIR=$DATASET_DIR/$SCENE_NAME
    COLMAP_PATH=$SCENE_DIR/colmap
    OPENMVS_DIR=$SCENE_DIR/openmvs
    
    # Downsample images
    python neverwhere_envs/mv_sample_images.py -i $SCENE_DIR -d 2
    ```

1. Extract pose using COLMAP:
    ```bash
    # Run COLMAP pipeline using our custom runner
    python neverwhere_envs/runners/colmap_runner.py \
        --img-dir $SCENE_DIR/images \
        --output-dir $COLMAP_PATH
    ```

    This will run COLMAP's feature extraction, matching, and sparse reconstruction pipeline to generate camera poses and a sparse point cloud.

2. Run OpenMVS to get textured Mesh
    ```bash
    # Run OpenMVS pipeline (includes COLMAP interface and mesh generation)
    python neverwhere_envs/runners/openmvs_runner.py \
        --img-dir $SCENE_DIR/images \
        --working-dir $OPENMVS_DIR \
        --colmap-dir $COLMAP_PATH
    ```

3. Process Collision Geometry
    Convert the refined mesh model to OBJ format for use as collision geometry in MuJoCo.

    ```bash
    python neverwhere_envs/process_collision.py \
        -i $OPENMVS_DIR/model_dense_mesh_refine.ply \
        -o $SCENE_DIR/collision.obj
    ```

4. Extract Mesh's Vertices for Gaussian Initialization
    Firstly, run: `mv $SCENE_DIR/colmap/sparse_pc.ply $SCENE_DIR/colmap/colmap_pc.ply`

    **Option 1: With Combining (Default)**

    This option extracts the mesh's vertices and combines them with the COLMAP point cloud. This is the default behavior.

    ```bash
    mv $SCENE_DIR/colmap/sparse_pc.ply $SCENE_DIR/colmap/colmap_pc.ply
    python neverwhere_envs/extract_gsplat_init.py \
        -i $OPENMVS_DIR/model_dense_mesh_refine_texture.ply \
        -t $OPENMVS_DIR/model_dense_mesh_refine_texture0.png \
        -o $SCENE_DIR/colmap/sparse_pc.ply \
        -c $SCENE_DIR/colmap/colmap_pc.ply
    ```

    The `-c` or `--combine` option specifies the COLMAP point cloud file to combine with the extracted mesh vertices. By default, it combines with the renamed COLMAP point cloud.

    **Option 2: Without Combining**

    If you prefer to extract the mesh's vertices without combining with the COLMAP point cloud, you can omit the `-c` option:

    ```bash
    mv $SCENE_DIR/colmap/sparse_pc.ply $SCENE_DIR/colmap/colmap_pc.ply
    python neverwhere_envs/extract_gsplat_init.py \
        -i $OPENMVS_DIR/model_dense_mesh_refine_texture.ply \
        -t $OPENMVS_DIR/model_dense_mesh_refine_texture0.png \
        -o $SCENE_DIR/colmap/sparse_pc.ply
    ```

    Choose the option that best suits your needs for initializing the Gaussian Splatting process. The default (Option 1) is recommended for most use cases as it combines the mesh vertices with the COLMAP point cloud.

5. Run NerfStudio's SplatFacto to get the trained 3DGS
   ```bash
   ns-train splatfacto-big --data $SCENE_DIR/nerfstudio_data/colmap/transforms.json \
       --output-dir $SCENE_DIR/gsplat \
       --pipeline.model.cull_alpha_thresh=0.05 \
       --pipeline.model.densify_grad_thresh=0.0008 \
       --pipeline.model.stop_split_at=30000 \
       --pipeline.model.max_gauss_ratio=5.0 \
       --pipeline.model.use_scale_regularization=True \
       --vis=tensorboard
   ```
   Note: We do not use scene pose auto-scale or auto-orientation to maintain alignment with OpenMVS. This eliminates the need for subsequent mesh alignment with the 3DGS model.


#### Option 2: Polycam Process

1. Extract pose
    ```bash
    SCENE_NAME=your_scene_name
    DATASET_DIR=$PYTHONPATH/neverwhere_envs/datasets
    SCENE_DIR=$DATASET_DIR/$SCENE_NAME
    IMAGES_PATH=$SCENE_DIR/polycam
    POLYCAM_PATH=$SCENE_DIR/nerfstudio_data/polycam

    ns-process-data polycam --data $IMAGES_PATH --output-dir $POLYCAM_PATH --num_downscales 0
    ```

2. Prepare Polycam data for OpenMVS
    ```bash
    OPENMVS_DIR=$SCENE_DIR/openmvs_outputs/polycam
    mkdir -p $OPENMVS_DIR

    # Interface Polycam
    InterfacePolycam -i $IMAGES_PATH/keyframes -o $OPENMVS_DIR/model_polycam.mvs

    # Run OpenMVS pipeline
    python neverwhere_envs/openmvs_runner.py \
        --working-dir $OPENMVS_DIR \
        --input-mvs $OPENMVS_DIR/model_polycam.mvs \
        --is-colmap False
    ```

3. Run OpenMVS to get textured Mesh
    ```bash
    # Densify Point Cloud
    DensifyPointCloud -i $OPENMVS_DIR/model_polycam.mvs \
        -o $OPENMVS_DIR/model_dense.mvs \
        -w $OPENMVS_DIR \
        --resolution-level 0 --max-resolution 256 \
        -v 1

    # Reconstruct Mesh
    ReconstructMesh -i $OPENMVS_DIR/model_dense.mvs \
        -o $OPENMVS_DIR/model_dense_recon.mvs \
        -w $OPENMVS_DIR

    # Refine Mesh
    RefineMesh -i $OPENMVS_DIR/model_dense.mvs \
        -m $OPENMVS_DIR/model_dense_recon.ply \
        -o $OPENMVS_DIR/model_dense_mesh_refine.mvs \
        -w $OPENMVS_DIR \
        --scales 1 \
        --max-face-area 16

    # Texture Mesh
    TextureMesh $OPENMVS_DIR/model_dense.mvs \
        -m $OPENMVS_DIR/model_dense_mesh_refine.ply \
        -o $OPENMVS_DIR/model_dense_mesh_refine_texture.mvs \
        -w $OPENMVS_DIR
    ```

4. Process Collision Geometry
    ```bash
    python neverwhere_envs/process_collision.py \
        -i $OPENMVS_DIR/model_dense_mesh_refine.ply \
        -o $SCENE_DIR/collision_polycam.obj
    ```

5. Extract Mesh's Vertices for Gaussian Initialization
    ```bash
    ```

6. Run NerfStudio's SplatFacto to get the trained 3DGS
   ```bash
   ns-train splatfacto-big --data $SCENE_DIR/nerfstudio_data/polycam/transforms.json \
       --output-dir $SCENE_DIR/gsplat_polycam \
       --pipeline.model.cull_alpha_thresh=0.05 \
       --pipeline.model.densify_grad_thresh=0.0008 \
       --pipeline.model.stop_split_at=30000 \
       --pipeline.model.max_gauss_ratio=5.0 \
       --pipeline.model.use_scale_regularization=True \
       --vis=tensorboard
   ```