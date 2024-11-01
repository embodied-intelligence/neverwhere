import random

import dm_control
import numpy as np
import torch
from collections import defaultdict, deque
from importlib import import_module
from logging import warning
from matplotlib.cm import get_cmap
from ml_logger.job import RUN
from params_proto import Flag, ParamsProto, Proto
from pickle import UnpicklingError
from tqdm import trange

import neverwhere

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]


class Unroll(ParamsProto, prefix="unroll"):
    env_name: str = Proto("lcs:Go1-flat_vision-v1")
    checkpoint: str = Proto(
        "/lucid-sim/lucid-sim/scripts/train/2024-01-19/23.48.06/go1_flat/200/checkpoints/model_last.pt",
        help="Path to the model checkpoint.",
    )
    offline_mode: bool = Flag("Run the model in offline mode, with downloaded checkpoint.")
    vision_key = Proto(None, help="default does not pass in image observation")

    model_entrypoint = "cxx.modules.parkour_actor:get_parkour_teacher_policy"

    num_steps = 800
    seed = 100

    delay = 0
    action_delay = 1

    render = Flag("flag for rendering videos")

    log_metrics = Proto(True, help="save the episodic metrids to a results table.")

    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def main(_deps=None, **deps):
    from ml_logger import logger

    # fixme: temporary patch
    if _deps is not None:
        if _deps.get("Unroll.model_entrypoint", None) is None:
            Unroll.model_entrypoint = "cxx.modules.parkour_actor:get_parkour_teacher_policy"

    Unroll._update(_deps, **deps)

    try:  # RUN.prefix is a template, will raise error.
        RUN._update(_deps)
        logger.configure(RUN.prefix)
    except KeyError:
        pass

    logger.job_started(Unroll=vars(Unroll))
    print(logger.get_dash_url())

    logger.upload_file(__file__)

    if Unroll.render:
        logger.log_text(
            """
            keys:
            - Unroll.env_name
            - Unroll.delay
            - Unroll.seed
            charts:
            - type: video
              glob: splat_rgb.mp4
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
    np.random.seed(Unroll.seed)
    torch.manual_seed(Unroll.seed)
    random.seed(Unroll.seed)

    # spawn_pose = None
    initial_state = None
    if _deps is not None:
        # spawn_pose = _deps.get("spawn_pose", None)
        initial_state = _deps.get("initial_state", None)

    # spawn_pose = deps.get("spawn_pose", spawn_pose)
    initial_state = deps.get("initial_state", initial_state)

    env = neverwhere.make(Unroll.env_name, device=Unroll.device, random=Unroll.seed, initial_state=initial_state)

    module_path = Unroll.model_entrypoint
    module_name, entrypoint = module_path.split(":")
    module = import_module(module_name)
    model_entrypoint = getattr(module, entrypoint)

    try:
        actor = model_entrypoint()
        state_dict = logger.torch_load(Unroll.checkpoint, map_location=Unroll.device)
        actor.load_state_dict(state_dict)
    except (UnpicklingError, AssertionError, TypeError):
        warning("Alternative loading scheme. This will be deprecated soon. Please re-train!")
        actor = logger.torch_load(Unroll.checkpoint)
        actor.last_latent = torch.zeros((1, 32)).float().to(Unroll.device)

    actor.to(Unroll.device)
    actor.eval()

    cmap = get_cmap("Spectral")

    b = defaultdict(lambda: [])
    visual_buffer = None  # deque([None] * 5, maxlen=5)
    action_buffer = deque([np.zeros(12)] * 5, maxlen=5)

    latent = None
    env.reset()

    progress = 0

    for i in trange(Unroll.num_steps):
        try:
            # obs, reward, done, info = env.step(action, update_baseline=True)
            obs, reward, done, info = env.step(action_buffer[-1 - Unroll.action_delay])
            if done:
                print("Env reset, ending this trial.")
                break
            progress += 1
        except dm_control.rl.control.PhysicsError:
            print("Physics Error, ending this trial.")
            break

        ego_view = info.get(Unroll.vision_key, None)

        if visual_buffer is None:
            visual_buffer = deque([ego_view] * 10, maxlen=10)
        else:
            visual_buffer.append(ego_view)

        obs_input = torch.from_numpy(obs).float()

        ego_view = visual_buffer[-1 - Unroll.delay]

        with torch.no_grad():
            # ego_view = torch.zeros_like(ego_view)
            action, *extra = actor(
                ego_view,
                obs_input.to(Unroll.device),
                vision_latent=latent,
            )

            if len(extra) > 0:
                latent = extra[0]

            action = action.cpu().numpy()
            action_buffer.append(action)

        if not Unroll.render:
            continue

        if "heightmap" in info:
            hp = info["heightmap"]
            hp -= hp.min()
            hp /= hp.max() + 0.01
            hp = cmap(hp)
            b["heightmaps"].append(hp)

        if "height_samples" in info:
            hp = info["height_samples"]
            hp -= hp.min()
            hp /= hp.max() + 0.01
            hp = cmap(hp)
            b["height_samples"].append(hp)

        if "segmented_img" in info:
            segmentation_viz = info["segmented_img"]
            b["segmentation"].append(segmentation_viz)

            for i, m in info["masks"].items():
                b[f"mask_{i}_in"].append(m[0])  # in, for group zero
                b[f"mask_{i}_out"].append(m[1])  # in, for group zero

        if "flow" in info:
            b["flow"].append(info["flow"])
            b["flow_mask"].append(info["flow_mask"])

            if "flow_image" in info:
                b["flow_viz"].append(info["flow_image"])

        if "render_rgb" in info:
            b["render_rgb"].append(info["render_rgb"])

        if "render_depth" in info:
            b["render_depth"].append(info["render_depth"])

        if "midas_depth" in info:
            b["midas_depth"].append(info["midas_depth"])

        if "splat_rgb" in info:
            b["splat_rgb"].append(info["splat_rgb"])

        if "splat_depth" in info:
            b["splat_depth"].append(info["splat_depth"])

        if Unroll.render:
            render = env.render(camera_id="tracking-2", width=640, height=300)
            b["renders"].append(render)
            ego_render = env.render(camera_id="ego-rgb", width=640, height=360)
            b["ego_renders"].append(ego_render)

    for k, frames in b.items():
        if frames[-1].dtype in ["float32", "float64"]:
            frames = np.stack(frames)
            frames /= max(frames.max(), frames.min())

        fps = 50 * len(frames) // progress
        print(f"saving video to {k}.mp4 at fps=", fps)
        logger.save_video(frames, f"{k}.mp4", fps=fps)

    if Unroll.log_metrics:
        # log performance
        episodic_metrics = env.unwrapped.env.task.get_metrics()
        logger.save_pkl(episodic_metrics, "episode_metrics.pkl", append=True)
        logger.print(episodic_metrics)


if __name__ == "__main__":
    job_kwargs = {
        'unroll.render': True,
        'unroll.log_metrics': True,
        'unroll.num_steps': 300,
        'unroll.vision_key': 'vision',
        'unroll.env_name': 'Real-heightmap-chase-real_flat_01_stata_grass',
        'unroll.checkpoint': '/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt',
        'unroll.seed': 0,
        'RUN.job_counter': 1,
        'RUN.prefix': 'neverwhere/neverwhere/ziyu_playground/1101/Real-heightmap-chase-real_flat_01_stata_grass',
        'RUN.job_name': 'Real-heightmap-chase-real_flat_01_stata_grass'
    }
    main(job_kwargs)
