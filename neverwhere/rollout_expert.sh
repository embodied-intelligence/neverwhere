GPU_ID=$1
SCENE_NAME=$2

export PYTHONPATH="$(pwd)/../parkour:$(pwd)"
export CUDA_VISIBLE_DEVICES="$GPU_ID"
export ML_LOGGER_ROOT="http://escher.csail.mit.edu:4000"
export ML_LOGGER_USER="ziyuchen"
export NEVERWHERE_EVAL_DATASETS="$(pwd)/neverwhere/tasks/real_scenes"
export MUJOCO_GL="egl"
export MUJOCO_EGL_DEVICE_ID="$GPU_ID"

ENV_NAME="Neverwhere-heightmap-${SCENE_NAME}-cones"
PREFIX="neverwhere/neverwhere/rollout_expert/${SCENE_NAME}"
python neverwhere/eval_teacher_parkour.py \
    --scene_name "$SCENE_NAME" \
    --env_name "$ENV_NAME" \
    --prefix "$PREFIX" \
    --times 50