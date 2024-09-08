from collections import defaultdict, deque
from importlib import import_module
from logging import warning

import dm_control
import numpy as np
import random
import torch
from PIL import Image
from dataclasses import dataclass
from params_proto import Flag, ParamsProto, Proto
from pickle import UnpicklingError
from tqdm import trange
from transforms3d import euler
from typing import Union

import lucidsim
from cxx.modules.parkour_actor import PolicyArgs
from lucidsim.wrappers.lucid_env import LucidEnv

# from workflows.hurdle_scene.imagen import Imagen

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]


@dataclass
class ImageMaker:
    """Operator for Converting Tensor into Images"""

    format: str = "PNG"

    def __matmul__(self, t: Union[torch.Tensor, np.ndarray]):
        """Convert Tensor into Images."""

        if isinstance(t, torch.Tensor):
            t = t.cpu().numpy()

        if t.dtype != "uint8":
            arr = (t * 255).astype("uint8")
        else:
            arr = t

        img = Image.fromarray(arr)

        # set the format to encourage compression
        img.format = self.format

        return img


class Unroll_stream(ParamsProto, prefix="unroll"):
    env_name: str = Proto("lcs:Go1-flat_vision-v1")
    rollout_id: str = Proto(help="Used for managing the collected data.")

    checkpoint: str = Proto(
        "/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
        help="Path to the model checkpoint.",
    )
    offline_mode: bool = Flag("Run the model in offline mode, with downloaded checkpoint.")
    vision_key = Proto(None, help="default does not pass in image observation")

    model_entrypoint = "cxx.modules.parkour_actor:get_parkour_teacher_policy"

    num_steps = 600

    delay = 0
    action_delay = 1

    stop_after_termination = True
    collect_states = Flag(help="when on, records the robot states in the simulator. Useful for telemetry.")

    render = Flag("flag for rendering videos")
    silent = Flag("flag for non-printing")

    seed = 100
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def get_tf_info(_deps=None, **deps):
    Unroll_stream._update(_deps, **deps)

    env = lucidsim.make(Unroll_stream.env_name, device=Unroll_stream.device, random=Unroll_stream.seed)

    while True:
        print("loading", end=">")
        if hasattr(env, "get_tf_info"):
            return env.get_tf_info()

        env = env.env
        if isinstance(env, LucidEnv):
            print("no transformation info is collected")
            break


def main(_deps=None, **deps):
    from ml_logger import logger

    Unroll_stream._update(_deps, **deps)

    logger.job_started(Unroll=vars(Unroll_stream))
    print(logger.get_dash_url())
    print(logger)

    logger.upload_file(__file__)

    Img = ImageMaker()
    Img_JPEG = ImageMaker(format="JPEG")

    if Unroll_stream.render:
        logger.log_text(
            """
            keys:
            - Unroll_stream.env_name
            - Unroll_stream.delay
            - Unroll_stream.seed
            charts:
            - type: video
              glob: vision.mp4
            - type: video
              glob: renders.mp4
            - type: video
              glob: ego_renders.mp4
            - type: video
              glob: heightmaps.mp4
            - type: video
              glob: height_samples.mp4
            """,
            ".charts.yml",
            True,
            True,
        )

    # set seeds
    np.random.seed(Unroll_stream.seed)
    torch.manual_seed(Unroll_stream.seed)
    random.seed(Unroll_stream.seed)

    env = lucidsim.make(Unroll_stream.env_name, device=Unroll_stream.device, random=Unroll_stream.seed)

    module_path = Unroll_stream.model_entrypoint
    module_name, entrypoint = module_path.split(":")
    module = import_module(module_name)
    model_entrypoint = getattr(module, entrypoint)

    # fixme (alany1): get rid of this one and put it into a separate entrypoint
    PolicyArgs.use_camera = Unroll_stream.vision_key is not None
    try:
        actor = model_entrypoint()
        state_dict = logger.torch_load(Unroll_stream.checkpoint, map_location=Unroll_stream.device)
        if state_dict is None:
            print(Unroll_stream.checkpoint)
        actor.load_state_dict(state_dict)
    except (UnpicklingError, AssertionError):
        warning("Alternative loading scheme. This will be deprecated soon. Please re-train!")
        actor = logger.torch_load(Unroll_stream.checkpoint)
        actor.last_latent = torch.zeros((1, 32)).float().to(Unroll_stream.device)

    actor.to(Unroll_stream.device)
    actor.eval()

    b = defaultdict(lambda: [])
    visual_buffer = deque([None] * 5, maxlen=5)
    action_buffer = deque([np.zeros(12)] * 5, maxlen=5)

    latent = None
    env.reset()

    unwrapped_env = env.unwrapped.env

    body_to_name = {body: unwrapped_env.physics.model.body(body).name for body in range(env.unwrapped.env.physics.model.nbody)}

    b = defaultdict(lambda: [])

    if Unroll_stream.silent:
        it = range(Unroll_stream.num_steps)
    else:
        it = trange(Unroll_stream.num_steps)

    for step in it:
        # fixme: remove update_baseline=True
        try:
            step_action = action_buffer[-1 - Unroll_stream.action_delay]
            obs, reward, done, info = env.step(step_action)

            # check if done
            if Unroll_stream.stop_after_termination:
                episodic_metrics = env.unwrapped.env.task.get_metrics()
                # note: set the stop_after_termination to False for Chase environments
                frac_goals_reached = episodic_metrics["frac_goals_reached"]

                if frac_goals_reached == 1.0:
                    done = True
                    print("All goals reached, ending this trial.")

            if done:
                print("Env reset, ending this trial.")
                break

        except dm_control.rl.control.PhysicsError:
            print("Physics Error, ending this trial.")
            break

        cam_pos = unwrapped_env.physics.named.data.cam_xpos["ego-rgb-render"]
        cam_rot = unwrapped_env.physics.named.data.cam_xmat["ego-rgb-render"]

        img_b = {}

        # if "vision" in info:
        #     # vision has [B, stack_dim, img_dim, H, W]
        #     img_b["vision"] = Img @ (info["vision"][0, 0].permute(1, 2, 0) + 0.5)

        if "render_depth" in info:
            img_b["render_depth"] = Img @ info["render_depth"]

        if "render_rgb" in info:
            # already uint8, no need to cast
            img_b["render_rgb"] = Img_JPEG @ info["render_rgb"]

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

        if "flow" in info:
            img_b["flow"] = Img @ info["flow"]
            img_b["flow_mask"] = Img @ info["flow_mask"]

        if "flow_image" in info:
            img_b["flow_image"] = Img @ info["flow_image"]

        if Unroll_stream.render:
            render = env.render(camera_id="tracking", width=640, height=300)
            img_b["render"] = Image.fromarray(render)
            ego_render = env.render(camera_id="ego-rgb-render", width=640, height=360)
            img_b["ego_render"] = Image.fromarray(ego_render)
            # if ego_view is not None:
            #     b["vision"].append(ego_view.permute([1, 2, 0]).cpu().numpy())

        # todo: use _ to set the update_baselines

        if "teacher_obs" in info:
            # for keeping track of scandot observations
            observations = info["teacher_obs"].copy()
        else:
            observations = obs.copy()

        state_dict = {}
        if Unroll_stream.collect_states:
            # state_dict = {
            #     "pos": env.unwrapped.env.physics.data.qpos[:3].copy(),
            #     "quat": env.unwrapped.env.physics.data.qpos[3:7].copy(),
            #     "joints": env.unwrapped.env.physics.data.qpos[7 : 7 + 12].copy(),
            # }

            for body, name in body_to_name.items():
                pos = unwrapped_env.physics.data.xpos[body].copy().tolist()
                quat = unwrapped_env.physics.data.xquat[body].copy()
                state_dict[name] = (pos, euler.quat2euler(quat))

        generated_image = yield {
            **img_b,
            "obs": observations,
            "cam_pos": cam_pos.copy(),
            "cam_rot": cam_rot.copy(),
            "states": state_dict,
            "sim_state": info.get("sim_state", None),
        }

        if generated_image is not None:
            # this is a special function belonging to the lucid dreams wrapper, indicates streaming mode
            generated_image = np.array(generated_image)
            ego_view = env.update_vision(generated_image)
        else:
            ego_view = info.get(Unroll_stream.vision_key, None)

        visual_buffer.append(ego_view)
        obs_input = torch.from_numpy(obs).float()
        ego_view = visual_buffer[-1 - Unroll_stream.delay]

        with torch.no_grad():
            action, *extras = actor(
                ego_view,
                obs_input.to(Unroll_stream.device),
                vision_latent=latent,
            )

            if len(extras) > 0:
                latent = extras[0]

            action = action.cpu().numpy()
            action_buffer.append(action)


if __name__ == "__main__":
    from ml_logger import logger

    frames = []
    depths = []
    gen = main(
        env_name="Extensions-cones-stairs_wh-lucidsim_sampling-v1",
        model_cls="behavior_cloning.go1_model.transformers.transformer_policy:TransformerPolicy",
        checkpoint="/alanyu/scratch/2024/05-18/152233/checkpoints/net_50.pt",
        vision_key="vision",
        stop_after_termination=False,
        render=True,
        seed=3,
        num_steps=100,
    )

    data = next(gen)

    while True:
        try:
            # generate
            generated = np.random.randn(80, 45, 3)
            frames.append(generated)
            data = gen.send(generated)
            depths.append(data["render_depth"])

        except StopIteration:
            print(len(frames))
            logger.save_video(frames, "rgb.mp4", fps=50)
            logger.save_video(depths, "depth.mp4", fps=50)
            break
