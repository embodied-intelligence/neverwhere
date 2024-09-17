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
    IMAGES_PATH=$SCENE_DIR/polycam/keyframes/correct_images
    if [ ! -d "$IMAGES_PATH" ]; then
        IMAGES_PATH=$SCENE_DIR/polycam/keyframes/images
    fi
    OUTPUT_PATH=$SCENE_DIR/nerfstudio_data/colmap
    MESH_DIR=$SCENE_DIR/mesh_openmvs

    # Step 1: Extract pose
    ns-process-data images --data $IMAGES_PATH --output-dir $OUTPUT_PATH --matching-method exhaustive --num_downscales 0 --camera_type pinhole

    # Step 2: Prepare colmap data for OpenMVS
    colmap model_converter --input_path $OUTPUT_PATH/colmap/sparse/0 --output_path $OUTPUT_PATH/colmap/sparse --output_type TXT

    # Step 3: Run OpenMVS to get textured Mesh
    InterfaceCOLMAP -w $MESH_DIR -i $OUTPUT_PATH/colmap/ -o $MESH_DIR/model_colmap.mvs
    ln -s $OUTPUT_PATH/images $MESH_DIR/images
    DensifyPointCloud -i $MESH_DIR/model_colmap.mvs -o $MESH_DIR/model_dense.mvs -w $MESH_DIR -v 1
    ReconstructMesh -i $MESH_DIR/model_dense.mvs -p $MESH_DIR/model_dense.ply -o $MESH_DIR/model_dense_recon.mvs -w $MESH_DIR
    RefineMesh -i $MESH_DIR/model_dense.mvs -m $MESH_DIR/model_dense_recon.ply -o $MESH_DIR/model_dense_mesh_refine.mvs -w $MESH_DIR --scales 1 --max-face-area 16
    TextureMesh $MESH_DIR/model_dense.mvs -m $MESH_DIR/model_dense_mesh_refine.ply -o $MESH_DIR/model_dense_mesh_refine_texture.mvs -w $MESH_DIR

    # Step 4: Extract Mesh's Vertices for Gaussian Initialization
    mv $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply $SCENE_DIR/nerfstudio_data/colmap/colmap_pc.ply
    python neverwhere_envs/extract_gsplat_init.py -i $MESH_DIR/model_dense_mesh_refine_texture.ply -t $MESH_DIR/model_dense_mesh_refine_texture0.png -o $SCENE_DIR/nerfstudio_data/colmap/sparse_pc.ply -c $SCENE_DIR/nerfstudio_data/colmap/colmap_pc.ply

    # Step 5: Run NerfStudio's SplatFacto to get the trained 3DGS
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