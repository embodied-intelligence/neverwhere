import os
import random
import argparse
from collections import defaultdict, deque
from importlib import import_module
from logging import warning
from pickle import UnpicklingError

import dm_control
import numpy as np
import torch
from matplotlib.cm import get_cmap
from ml_logger import logger
from ml_logger.job import RUN
from params_proto import Flag, ParamsProto, Proto
from tqdm import trange

import neverwhere
from cxx.modules.parkour_actor import PolicyArgs
from neverwhere.utils.log import save_video, save_image

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]

SAVE_TO_LOCAL = False

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
            - Unroll.times
            charts:
            - type: video
              glob: "*/splat_rgb.mp4"
            - type: video
              glob: "*/renders.mp4"
            - type: video
              glob: ego_renders.mp4
            - type: video
              glob: heightmaps.mp4
            - type: video
              glob: height_samples.mp4
            - yKeys: ["frac_goals_reached"]
              xKey: run
              yDomain: [0, 1]
            """,
            ".charts.yml",
            True,
            True,
        )

    all_metrics = []
    for unroll_idx in range(Unroll.times):
        # set seed
        seed = Unroll.seed + unroll_idx
        
        # set seeds
        np.random.seed(seed)
        torch.manual_seed(seed)
        random.seed(seed)

        # spawn_pose = None
        initial_state = None
        if _deps is not None:
            # spawn_pose = _deps.get("spawn_pose", None)
            initial_state = _deps.get("initial_state", None)

        # spawn_pose = deps.get("spawn_pose", spawn_pose)
        initial_state = deps.get("initial_state", initial_state)

        if RUN.scene_version == 'lucidsim':
            env = neverwhere.make_lucidsim(Unroll.env_name, device=Unroll.device, random=seed, initial_state=initial_state)
        else:
            env = neverwhere.make(Unroll.env_name, device=Unroll.device, random=seed, initial_state=initial_state)
        
        if SAVE_TO_LOCAL:
            os.makedirs(f"./{Unroll.env_name}/debug", exist_ok=True)

        module_path = Unroll.model_entrypoint
        module_name, entrypoint = module_path.split(":")
        module = import_module(module_name)
        model_entrypoint = getattr(module, entrypoint)

        PolicyArgs.use_camera = Unroll.vision_key is not None
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
            frame_id = i
            try:
                # obs, reward, done, info = env.step(action, update_baseline=True)
                obs, reward, done, info = env.step(action_buffer[-1 - Unroll.action_delay])
                
                # check if goal is reached
                episodic_metrics = env.unwrapped.env.task.get_metrics()
                frac_goals_reached = episodic_metrics['frac_goals_reached']
                if frac_goals_reached == 1.0:
                    done = True
                    print("Goal reached, ending this trial.")
                
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
            
            if Unroll.render:
                render = env.render(camera_id="tracking-2", width=640, height=300)
                b["renders"].append(render)
                if SAVE_TO_LOCAL:
                    save_image(render, os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_render.png"))
                    
                ego_render = env.render(camera_id="ego-rgb", width=640, height=360)
                b["ego_renders"].append(ego_render)
                if SAVE_TO_LOCAL:
                    save_image(ego_render, os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_ego_render.png"))
            else:
                continue

            if "heightmap" in info:
                hp = info["heightmap"]
                hp -= hp.min()
                hp /= hp.max() + 0.01
                hp = cmap(hp)
                b["heightmaps"].append(hp)
                if SAVE_TO_LOCAL:
                    save_image(hp, os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_heightmap.png"))

            if "height_samples" in info:
                hp = info["height_samples"]
                hp -= hp.min()
                hp /= hp.max() + 0.01
                hp = cmap(hp)
                b["height_samples"].append(hp)
                if SAVE_TO_LOCAL:
                    save_image(hp, os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_height_samples.png"))

            if "segmented_img" in info:
                segmentation_viz = info["segmented_img"]
                b["segmentation"].append(segmentation_viz)
                if SAVE_TO_LOCAL:
                    save_image(segmentation_viz, os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_segmentation.png"))

                for i, m in info["masks"].items():
                    b[f"mask_{i}_in"].append(m[0])  # in, for group zero
                    b[f"mask_{i}_out"].append(m[1])  # in, for group zero

            if "flow" in info:
                b["flow"].append(info["flow"])
                b["flow_mask"].append(info["flow_mask"])
                if SAVE_TO_LOCAL:
                    save_image(info["flow"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_flow.png"))
                    save_image(info["flow_mask"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_flow_mask.png"))

                if "flow_image" in info:
                    b["flow_viz"].append(info["flow_image"])
                    if SAVE_TO_LOCAL:
                        save_image(info["flow_image"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_flow_viz.png"))

            if "render_rgb" in info:
                b["render_rgb"].append(info["render_rgb"])
                if SAVE_TO_LOCAL:
                    save_image(info["render_rgb"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_render_rgb.png"))

            if "render_depth" in info:
                b["render_depth"].append(info["render_depth"])
                if SAVE_TO_LOCAL:
                    save_image(info["render_depth"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_render_depth.png"))

            if "midas_depth" in info:
                b["midas_depth"].append(info["midas_depth"])
                if SAVE_TO_LOCAL:
                    save_image(info["midas_depth"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_midas_depth.png"))

            if "splat_rgb" in info:
                b["splat_rgb"].append(info["splat_rgb"])
                if SAVE_TO_LOCAL:
                    save_image(info["splat_rgb"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_splat_rgb.png"))

            if "splat_depth" in info:
                b["splat_depth"].append(info["splat_depth"])
                if SAVE_TO_LOCAL:
                    save_image(info["splat_depth"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_splat_depth.png"))
                    
            if "pointclouds" in info:
                b["pointclouds"].append(info["pointclouds"])
                if SAVE_TO_LOCAL:
                    save_image(info["pointclouds"], os.path.join(f"./{Unroll.env_name}/debug", f"{unroll_idx}/{frame_id:04d}_pointclouds.png"))

        for k, frames in b.items():
            if frames[-1].dtype in ["float32", "float64"]:
                frames = np.stack(frames)
                frames /= max(frames.max(), frames.min())

            fps = 50 * len(frames) // progress
            print(f"saving video to {k}.mp4 at fps=", fps)
            logger.save_video(frames, f"{unroll_idx}/{k}.mp4", fps=fps)
            if SAVE_TO_LOCAL:
                save_video(frames, f"./{Unroll.env_name}", f"{unroll_idx}/{k}.mp4", fps=fps)

        if Unroll.log_metrics:
            # log performance
            episodic_metrics = env.unwrapped.env.task.get_metrics()
            all_metrics.append(episodic_metrics)
            logger.log_metrics_summary(key_values={"run": unroll_idx, "frac_goals_reached": episodic_metrics["frac_goals_reached"]})
            logger.save_pkl(episodic_metrics, f"{unroll_idx}/episode_metrics.pkl", append=True)
            logger.print(episodic_metrics)
    
    logger.print(f"avg success rate: {sum([i['frac_goals_reached'] for i in all_metrics]) / len(all_metrics)}")


if __name__ == "__main__":
    # lucidsim examples
    # for env_name in [
    #     "Real-heightmap-chase-real_flat_01_stata_grass",
    #     "Real-heightmap-chase-real_flat_02_wh_evening", 
    #     "Real-heightmap-chase-real_flat_03_stata_indoor"
    # ]:
    #     job_kwargs = {
    #         'unroll.render': True,
    #         'unroll.log_metrics': True,
    #         'unroll.num_steps': 300,
    #         'unroll.vision_key': 'vision',
    #         'unroll.env_name': env_name,
    #         'unroll.checkpoint': '/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt',
    #         'unroll.seed': 0,
    #         'RUN.job_counter': 1,
    #         'RUN.prefix': f'neverwhere/neverwhere/ziyu_playground/1101/{env_name}',
    #         'RUN.job_name': env_name,
    #         'RUN.scene_version': 'lucidsim'
    #     }
    #     main(job_kwargs)
    
    # for env_name in [
    #     "Real-heightmap-hurdle_one_blue_carpet_v2-cones",
    #     "Real-heightmap-hurdle_one_dark_grassy_courtyard_v1-cones", 
    #     "Real-heightmap-hurdle_one_light_grassy_courtyard_v3-cones"
    # ]:
    #     job_kwargs = {
    #         'unroll.render': True,
    #         'unroll.log_metrics': True,
    #         'unroll.num_steps': 500,
    #         'unroll.vision_key': None,
    #         'unroll.delay': 0,
    #         'unroll.seed': 500,
    #         'unroll.env_name': env_name,
    #         'unroll.checkpoint': '/lucid-sim/lucid-sim/baselines/launch_intermediate_ckpts_v3/go1/delay_4/300/checkpoints/model_last.pt',
    #         'RUN.job_counter': 1,
    #         'RUN.prefix': f'neverwhere/neverwhere/ziyu_playground/1101/{env_name}',
    #         'RUN.job_name': env_name,
    #         'RUN.scene_version': 'lucidsim'
    #     }
    #     main(job_kwargs)
    
    # neverwhere examples
    # available_scenes_list = open("neverwhere_envs/waitlist.txt").read().splitlines()
    # for scene_name in available_scenes_list:
    #     env_name = f"Neverwhere-heightmap-{scene_name}-cones" 
    #     job_kwargs = {
    #         'unroll.render': True,
    #         'unroll.log_metrics': True,
    #         'unroll.num_steps': 400,
    #         'unroll.vision_key': None,
    #         'unroll.env_name': env_name,
    #         'unroll.checkpoint': '/lucid-sim/lucid-sim/baselines/launch_intermediate_ckpts_v3/go1/delay_4/300/checkpoints/model_last.pt',
    #         'unroll.seed': 0,
    #         'RUN.job_counter': 1,
    #         'RUN.prefix': f'neverwhere/neverwhere/ziyu_playground/test_01072025/{env_name}',
    #         'RUN.job_name': env_name,
    #         'RUN.scene_version': 'neverwhere'
    #     }
    #     main(job_kwargs)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene_name", type=str, default="hurdle_226_blue_carpet_v3")
    parser.add_argument("--prefix", type=str, default="neverwhere/neverwhere/rollout_expert")
    parser.add_argument("--scene_version", type=str, default="neverwhere")
    parser.add_argument("--checkpoint", type=str, default="/lucid-sim/lucid-sim/baselines/launch_intermediate_ckpts_v3/go1/delay_4/300/checkpoints/model_last.pt")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--times", type=int, default=1)
    parser.add_argument("--num_steps", type=int, default=400)
    parser.add_argument("--vision_key", type=str, default=None)
    parser.add_argument("--env_name", type=str, default="Neverwhere-heightmap-hurdle_226_blue_carpet_v3-cones")
    parser.add_argument("--render", type=bool, default=True)
    parser.add_argument("--log_metrics", type=bool, default=True)
    args = parser.parse_args()

    job_kwargs = {
        'unroll.render': args.render,
        'unroll.log_metrics': args.log_metrics,
        'unroll.num_steps': args.num_steps,
        'unroll.vision_key': args.vision_key,
        'unroll.env_name': args.env_name,
        'unroll.checkpoint': args.checkpoint,
        'unroll.seed': args.seed,
        'RUN.job_counter': 1,
        'RUN.prefix': args.prefix,
        'RUN.job_name': args.env_name,
        'RUN.scene_version': args.scene_version,
        'unroll.times': args.times
    }
    
    main(job_kwargs)