#!/bin/bash

# Activate conda environment and set PYTHONPATH
# conda activate nerfstudio
export PYTHONPATH=$(pwd)

# Read scene names from valid_scans.txt
VALID_SCANS_FILE="$PYTHONPATH/neverwhere_envs/valid_scans.txt"
SCENE_NAMES=($(cat $VALID_SCANS_FILE))

for SCENE_NAME in "${SCENE_NAMES[@]}"; do
    echo "Processing scene: $SCENE_NAME"

    # Set up directories
    DATASET_DIR=$PYTHONPATH/neverwhere_envs/datasets
    SCENE_DIR=$DATASET_DIR/$SCENE_NAME
    IMAGES_PATH=$SCENE_DIR/raw_images
    COLMAP_PATH=$SCENE_DIR/nerfstudio_data/colmap
    OPENMVS_DIR=$SCENE_DIR/openmvs_outputs/colmap

    # Step 0: Downsample and Move Polycam Keyframes
    python neverwhere_envs/mv_sample_images.py -i $SCENE_DIR -d 2

    # Step 1: Extract pose
    ns-process-data images --data $IMAGES_PATH --output-dir $COLMAP_PATH --matching-method sequential --num_downscales 0 --camera_type pinhole

    # Step 2: Prepare colmap data for OpenMVS
    colmap model_converter --input_path $COLMAP_PATH/colmap/sparse/0 --output_path $COLMAP_PATH/colmap/sparse --output_type TXT

    # Step 3: Run OpenMVS to get textured Mesh
    InterfaceCOLMAP -w $OPENMVS_DIR -i $COLMAP_PATH/colmap/ -o $OPENMVS_DIR/model_colmap.mvs
    ln -s $COLMAP_PATH/images $OPENMVS_DIR/images
    DensifyPointCloud -i $OPENMVS_DIR/model_colmap.mvs -o $OPENMVS_DIR/model_dense.mvs -w $OPENMVS_DIR -v 1
    ReconstructMesh -i $OPENMVS_DIR/model_dense.mvs -p $OPENMVS_DIR/model_dense.ply -o $OPENMVS_DIR/model_dense_recon.mvs -w $OPENMVS_DIR
    RefineMesh -i $OPENMVS_DIR/model_dense.mvs -m $OPENMVS_DIR/model_dense_recon.ply -o $OPENMVS_DIR/model_dense_mesh_refine.mvs -w $OPENMVS_DIR --scales 1 --max-face-area 16
    TextureMesh $OPENMVS_DIR/model_dense.mvs -m $OPENMVS_DIR/model_dense_mesh_refine.ply -o $OPENMVS_DIR/model_dense_mesh_refine_texture.mvs -w $OPENMVS_DIR

    # Step 4: Process Collision Geometry
    python neverwhere_envs/process_collision.py -i $OPENMVS_DIR/model_dense_mesh_refine.ply -o $SCENE_DIR/collision.obj

    # Step 5: Extract Mesh's Vertices for Gaussian Initialization
    mv $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply $SCENE_DIR/nerfstudio_data/colmap/colmap_pc.ply
    python neverwhere_envs/extract_gsplat_init.py -i $OPENMVS_DIR/model_dense_mesh_refine_texture.ply -t $OPENMVS_DIR/model_dense_mesh_refine_texture0.png -o $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply -c $SCENE_DIR/nerfstudio_data/colmap/colmap_pc.ply

    # Step 6: Run NerfStudio's SplatFacto to get the trained 3DGS
    ns-train splatfacto-big --data $SCENE_DIR/nerfstudio_data/colmap/transforms.json \
        --output-dir $SCENE_DIR/gsplat \
        --pipeline.model.cull_alpha_thresh=0.05 \
        --pipeline.model.densify_grad_thresh=0.0008 \
        --pipeline.model.stop_split_at=30000 \
        --pipeline.model.max_gauss_ratio=5.0 \
        --pipeline.model.use_scale_regularization=True \
        --vis=tensorboard

    echo "Finished processing scene: $SCENE_NAME"
done

echo "All scenes processed."