from collections import deque
from importlib import import_module
from logging import warning

import PIL
import dm_control
import math
import numpy as np
import random
import torch
from PIL import Image
from dataclasses import dataclass
from params_proto import ParamsProto, Proto
from pickle import UnpicklingError
from torch import TensorType
from tqdm import trange
from typing import Union

import lucidsim
from cxx.modules.parkour_actor import PolicyArgs
from lucidsim.utils.utils import pick
from lucidsim.wrappers.optical_flow_wrapper import OpticalFlowWrapper
from optical_flow import warp_forward

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]


@dataclass
class ImageMaker:
    """Operator for Converting Tensor into Images"""

    format: str = "PNG"

    def __matmul__(self, t: Union[torch.Tensor, np.ndarray]):
        """Convert Tensor into Images."""

        if t.dtype != "uint8":
            arr = (t * 255).astype("uint8")
        else:
            arr = t

        if isinstance(t, torch.Tensor):
            arr = arr.cpu().numpy()

        img = Image.fromarray(arr)

        # set the format to encourage compression
        img.format = self.format

        return img


class Unroll_flow_stream(ParamsProto, prefix="unroll"):
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

    vision_key = Proto(None, help="default does not pass in image observation")
    model_entrypoint = "cxx.modules.parkour_actor:get_parkour_teacher_policy"

    baseline_interval = 7

    num_steps = 600

    # if this is true, we will also render a third person view
    render = True

    delay = 0
    action_delay = 1

    stop_after_termination = True

    # Important: these need to match the image you are warping
    camera_name = "ego-rgb-render"
    width = 1280
    height = 768

    seed = 1
    device = "cuda" if torch.cuda.is_available() else "cpu"


def main(_deps=None, **deps):
    from ml_logger import logger

    Unroll_flow_stream._update(_deps, **deps)

    logger.job_started(Unroll_flow_stream=vars(Unroll_flow_stream))
    print(logger.get_dash_url())

    logger.upload_file(__file__)

    Img = ImageMaker()
    Img_JPEG = ImageMaker(format="JPEG")

    np.random.seed(Unroll_flow_stream.seed)
    torch.manual_seed(Unroll_flow_stream.seed)
    random.seed(Unroll_flow_stream.seed)

    env = lucidsim.make(
        Unroll_flow_stream.env_name,
        device=Unroll_flow_stream.device,
        random=Unroll_flow_stream.seed,
        optical_flow_camera=Unroll_flow_stream.camera_name,
    )
    env = OpticalFlowWrapper(
        env,
        width=Unroll_flow_stream.width,
        height=Unroll_flow_stream.height,
        camera_id=Unroll_flow_stream.camera_name,
        visualize=True,
    )

    module_path = Unroll_flow_stream.model_entrypoint
    module_name, entrypoint = module_path.split(":")
    module = import_module(module_name)
    model_entrypoint = getattr(module, entrypoint)

    # fixme (alany1): get rid of this one and put it into a separte entrypoint
    PolicyArgs.use_camera = Unroll_flow_stream.vision_key is not None
    try:
        actor = model_entrypoint()
        state_dict = logger.torch_load(Unroll_flow_stream.checkpoint, map_location=Unroll_flow_stream.device)
        actor.load_state_dict(state_dict)
    except (UnpicklingError, AssertionError):
        warning("Alternative loading scheme. This will be deprecated soon. Please re-train!")
        actor = logger.torch_load(Unroll_flow_stream.checkpoint)
        actor.last_latent = torch.zeros((1, 32)).float().to(Unroll_flow_stream.device)

    actor.to(Unroll_flow_stream.device)
    actor.eval()

    visual_buffer = None
    action_buffer = deque([np.zeros(12)] * 5, maxlen=5)
    latent = None

    env.reset()

    num_batches = math.ceil(Unroll_flow_stream.num_steps / Unroll_flow_stream.baseline_interval)
    baseline_t = None

    all_done = False

    for batch in trange(num_batches, desc="Generating flows"):
        # check done
        if all_done:
            break
        for substep in range(Unroll_flow_stream.baseline_interval):
            update_baseline = substep == 0

            try:
                step_action = action_buffer[-1 - Unroll_flow_stream.action_delay]
                obs, reward, all_done, info = env.step(step_action, update_baseline=update_baseline)

                # check if done
                if Unroll_flow_stream.stop_after_termination:
                    episodic_metrics = env.unwrapped.env.task.get_metrics()
                    # note: set the stop_after_termination to False for Chase environments
                    frac_goals_reached = episodic_metrics["frac_goals_reached"]

                    if frac_goals_reached == 1.0:
                        all_done = True
                        print("All goals reached, ending this trial.")

                if all_done:
                    print("Env reset, ending this trial.")
                    break

            except dm_control.rl.control.PhysicsError:
                print("Physics Error, ending this trial.")
                break

            cam_pos = env.unwrapped.env.physics.named.data.cam_xpos[Unroll_flow_stream.camera_name]
            cam_rot = env.unwrapped.env.physics.named.data.cam_xmat[Unroll_flow_stream.camera_name]

            img_b = {}

            if "render_depth" in info:
                img_b["render_depth"] = Img @ info["render_depth"]

            if "render_rgb" in info:
                # already uint8, no need to cast
                img_b["render_rgb"] = Img @ info["render_rgb"]

            # used for the MiDaS ControlNet
            if "midas_depth" in info:
                img_b["midas_depth"] = Img @ info["midas_depth"]

            if "splat_rgb" in info:
                # already uint8, no need to cast
                img_b["splat_rgb"] = info["splat_rgb"]

            if "masks" in info:
                if len(info["masks"]) == 3:
                    # three mask pipeline
                    img_b["foreground_mask"] = Img @ info["masks"][0][0]
                    img_b["cone_mask"] = Img @ info["masks"][1][0]
                    img_b["background_mask"] = Img @ info["masks"]["sky"][0]
                else:
                    mask_in, mask_out = info["masks"][0]
                    img_b["foreground_mask"] = Img @ mask_in
                    img_b["background_mask"] = Img @ mask_out

            if "teacher_obs" in info:
                # for keeping track of scandots observations
                observations = info["teacher_obs"].copy()
            else:
                observations = obs.copy()

            if Unroll_flow_stream.render:
                render = env.render(camera_id="tracking", width=1280, height=720)
                img_b["render"] = Image.fromarray(render)
                ego_render = env.render(camera_id="ego-rgb-render", width=1280, height=768)
                img_b["ego_render"] = Image.fromarray(ego_render)

            state_dict = {
                "pos": env.unwrapped.env.physics.data.qpos[:3].copy(),
                "quat": env.unwrapped.env.physics.data.qpos[3:7].copy(),
                "joints": env.unwrapped.env.physics.data.qpos[7 : 7 + 12].copy(),
            }

            flow_kwargs = pick(info, "flow_image", "flow", "flow_mask")
            if update_baseline:
                generated_image: PIL.Image = yield {
                    **img_b,
                    **state_dict,
                    **flow_kwargs,
                    "obs": observations,
                    "cam_pos": cam_pos.copy(),
                    "cam_rot": cam_rot.copy(),
                }

                generated_image_np = np.array(generated_image)

                baseline_t = torch.from_numpy(generated_image_np).permute(2, 0, 1).to(Unroll_flow_stream.device)
                baseline_t = baseline_t[None, ...].float()
                baseline_t /= 255

                baseline_t: TensorType["1xCxHxW", "float32"]
            else:
                flow_t = torch.from_numpy(flow_kwargs["flow"]).permute(2, 0, 1).to(Unroll_flow_stream.device)
                flow_t = flow_t[None, ...].float()

                generated_image_t, warping_mask = warp_forward(baseline_t, -flow_t, return_mask=True)

                generated_image_t = generated_image_t[0].permute(1, 2, 0)
                warping_mask = (1 - warping_mask[0, 0]).to(torch.bool)

                generated_image_np = generated_image_t.cpu().numpy()
                generated_image_np = (generated_image_np * 255).astype(np.uint8)

                # add alpha channel
                generated_image_np = np.concatenate([generated_image_np, np.ones_like(generated_image_np[..., :1]) * 255], axis=-1)
                generated_image_np[..., -1][flow_kwargs["flow_mask"].cpu().numpy()] = 0
                generated_image_np[..., -1][warping_mask.cpu().numpy()] = 0

                generated_image = Img @ generated_image_np

                yield dict(
                    generated_image=generated_image,
                    **img_b,
                    **state_dict,
                    **flow_kwargs,
                    obs=observations,
                    cam_pos=cam_pos.copy(),
                    cam_rot=cam_rot.copy(),
                )

            if Unroll_flow_stream.vision_key == "imagen":
                # this is a special function belonging to the lucid dreams wrapper, indicates streaming mode
                ego_view = env.update_vision(generated_image_np)
            else:
                ego_view = info.get(Unroll_flow_stream.vision_key, None)

            if visual_buffer is None:
                visual_buffer = deque([ego_view] * 10, maxlen=10)
            else:
                visual_buffer.append(ego_view)

            obs_input = torch.from_numpy(obs).float()
            ego_view = visual_buffer[-1 - Unroll_flow_stream.delay]

            with torch.no_grad():
                action, *extras = actor(
                    ego_view,
                    obs_input.to(Unroll_flow_stream.device),
                    vision_latent=latent,
                )

                if len(extras) > 0:
                    latent = extras[0]

                action = action.cpu().numpy()
                action_buffer.append(action)
