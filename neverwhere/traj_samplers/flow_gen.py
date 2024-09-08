import math
import numpy as np
import random
import torch
from params_proto import ParamsProto, Proto
from torch import TensorType
from tqdm import trange
from typing import List

import lucidsim
from lucidsim.utils.utils import pick
from lucidsim.wrappers.optical_flow_wrapper import OpticalFlowWrapper
from optical_flow import warp_forward

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]

from dm_control.mujoco.wrapper.mjbindings import mjlib


class FlowGen(ParamsProto, prefix="flow_gen"):
    """
    Provide a list of camera poses, return optical flow as a generator

    The seed is incredibly important, so that the geometry matches up.
    Also of course make sure that width, height, and camera FOV are correct as well
    """

    env_name: str = Proto("lcs:Go1-flat_vision-v1")
    checkpoint: str = Proto(
        "/lucid-sim/lucid-sim/scripts/train/2024-01-19/23.48.06/go1_flat/200/checkpoints/model_last.pt",
        help="Path to the model checkpoint.",
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"

    camera_name = "flow-cam"

    # in case there is terrain randomization
    baseline_interval = 5

    width = 1280
    height = 768

    seed = 1


def main(poses, source_images: List[TensorType], **deps):
    from ml_logger import logger

    FlowGen._update(**deps)

    logger.job_started(FlowGen=vars(FlowGen))
    print(logger.get_dash_url())

    np.random.seed(FlowGen.seed)
    torch.manual_seed(FlowGen.seed)
    random.seed(FlowGen.seed)

    env = lucidsim.make(FlowGen.env_name, device=FlowGen.device, random=FlowGen.seed, optical_flow_camera=FlowGen.camera_name)
    env = OpticalFlowWrapper(
        env,
        width=FlowGen.width,
        height=FlowGen.height,
        camera_id=FlowGen.camera_name,
        visualize=True,
    )

    env.reset()
    model = env.unwrapped.env.physics.named.model

    num_batches = math.ceil(len(poses) / FlowGen.baseline_interval)

    poses = iter(poses)
    source_images = iter(source_images)
    baseline_t = None
    for batch in trange(num_batches, desc="Generating flows"):
        for substep in range(FlowGen.baseline_interval):
            try:
                pos, rot = next(poses)
                source_img: TensorType["HxWxC", "uint8"] = next(source_images)

                # set pose
                quat = np.empty(4, dtype=np.float64)
                mjlib.mju_mat2Quat(quat, rot)

                update_baseline = substep == 0

                # Camera position update should go here because we want to prepare it for the OF processing,
                model.cam_pos[FlowGen.camera_name] = pos
                model.cam_quat[FlowGen.camera_name] = quat
                obs, unroll, done, info = env.step(np.zeros(12), update_baseline=update_baseline)

                flow_kwargs = pick(info, "flow_image", "flow", "flow_mask")

                if update_baseline:
                    warped = source_img.cpu().numpy()
                    baseline_t = source_img.permute(2, 0, 1)
                    # baseline_t = torch.from_numpy(baseline).permute(2, 0, 1).to(Unroll_flow_stream.device)
                    baseline_t = baseline_t[None, ...].float()
                    baseline_t /= 255
                else:
                    flow_t = torch.from_numpy(flow_kwargs["flow"]).permute(2, 0, 1).to(FlowGen.device)
                    flow_t = flow_t[None, ...].float()

                    warped = warp_forward(baseline_t, -flow_t)[0].permute(1, 2, 0)
                    warped[flow_kwargs["flow_mask"]] = 0

                    warped = warped.cpu().numpy()
                    warped = (warped * 255).astype(np.uint8)

                yield dict(warped=warped, **flow_kwargs)
            except StopIteration:
                print(f"Not evenly divisible by baseline_interval of {FlowGen.baseline_interval}, but OK!")
                break
