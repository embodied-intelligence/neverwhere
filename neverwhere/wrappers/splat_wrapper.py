import gym
import json
import numpy as np
import os
import torch

from neverwhere.gsplat.lucidsim_splat_model import Model
from neverwhere.utils.tf_utils import get_camera_extrinsic_matrix

DATASET_ROOT = os.environ.get("NEVERWHERE_EVAL_DATASETS")


def load_mesh_info(dataset_root, dataset_prefix):
    print("loading mesh info...")

    # extract scale
    dataparser_tf_path = f"{dataset_root}/{dataset_prefix}/transforms/dataparser_transforms.json"
    with open(dataparser_tf_path) as f:
        data = json.load(f)
        scale = data["scale"]
        print(data.keys())

    splat_mesh_tf_info = None
    if "splat_transform.json" in os.listdir(f"{dataset_root}/{dataset_prefix}/transforms"):
        splat_tf_path = f"{dataset_root}/{dataset_prefix}/transforms/splat_transform.json"
        with open(splat_tf_path) as f:
            data = json.load(f)
            print(data.keys())
            splat_tf = np.array(data["transform"])
            splat_scale = data["scale"]

            splat_mesh_tf_info = dict(transform=splat_tf, scale=splat_scale)

    print("mesh information is loaded!")
    return scale, splat_mesh_tf_info


def load_model(dataset_root, dataset_prefix, device):
    model = Model(device=device)

    print("loading model...")
    state_dict = torch.load(f"{dataset_root}/{dataset_prefix}/model.ckpt", map_location=device)["pipeline"]
    model.load_state_dict(state_dict, strict=False)
    model.eval()

    scale, splat_mesh_tf_info = load_mesh_info(dataset_root, dataset_prefix)

    return model, scale, splat_mesh_tf_info


class SplatWrapper(gym.Wrapper):
    """
    fill_masks: if True, will use the mask outputs from segmentation to fill in the splat render with the corresponding area from the rgb render.
    """

    def __init__(
        self,
        env,
        *,
        dataset_name,
        device,
        width=1280,
        height=768,
        camera_id="ego-rgb",
        splat_render_keys=["rgb"],
        fill_masks=True,
        near=0.0,
        far=5.0,
        **_,
    ):
        super().__init__(env)

        self.env = env

        self.width = width
        self.height = height
        self.camera_id = camera_id
        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[camera_id]

        self.fill_masks = fill_masks

        self.render_keys = splat_render_keys

        # for depth only
        self.near_clip = near
        self.far_clip = far

        self.fx = 0.5 * self.height / np.tan(self.fovy * np.pi / 360)
        self.fy = self.fx

        model_translation = self.unwrapped.env.physics.named.data.xpos["mesh"]

        # row major
        model_rot = self.unwrapped.env.physics.named.data.xmat["mesh"].reshape(3, 3)

        # self.scale: dataparser scale; only useful if using polycam poses
        self.model, self.scale, self.splat_info = load_model(DATASET_ROOT, dataset_name, device)

        # model_tf: splat to mujoco / poly to mujoco
        self.model_tf = np.eye(4)
        self.model_tf[:3, :3] = model_rot
        self.model_tf[:3, 3] = model_translation

        if self.splat_info is not None:
            splat_tf = self.splat_info["transform"]
            splat_scale = self.splat_info["scale"]

            # scale_mat = np.diag([1 / splat_scale, 1 / splat_scale, 1 / splat_scale, 1])
            scale_mat = np.diag([1 / splat_scale, 1 / splat_scale, 1 / splat_scale, 1])
            splat_tf = np.array(splat_tf).reshape(4, 4)

            # splat to poly
            # splat_tf = splat_tf @ scale_mat

            # model_tf: poly to mujoco
            # poly_to_mujoco @
            self.model_tf = self.model_tf @ scale_mat @ np.linalg.inv(splat_tf)
        else:
            scale_mat = np.diag([1 / self.scale, 1 / self.scale, 1 / self.scale, 1])

            # splat to poly
            self.model_tf = self.model_tf @ scale_mat

    def get_tf_info(self):
        """returns both the model transformation and the splat transformation if available."""
        try:
            return {
                "model_scale": self.scale,
                "model_matrix": self.model_tf.tolist(),
                "splat_scale": self.splat_info["scale"],
                "splat_matrix": self.splat_info["transform"].tolist(),
            }
        except (AttributeError, TypeError):
            return {
                "model_scale": self.scale,
                "model_matrix": self.model_tf.tolist(),
            }

    def splat_render(self, env_info: dict, cam_info: dict, *render_keys):
        outputs = self.model.get_simple_outputs(**cam_info)

        renders = {}
        if "rgb" in render_keys:
            raw_rgb = outputs["rgb"]
            rgb_np = (raw_rgb.clamp(0, 1) * 255).cpu().numpy()
            rgb_np = (rgb_np).astype(np.uint8)
            if self.fill_masks and "masks" in env_info and "render_rgb" in env_info:
                for group_id, (mask_in, mask_out) in env_info["masks"].items():
                    if group_id == "sky":
                        continue
                    rgb_np[mask_in] = env_info["render_rgb"][mask_in]
            renders["splat_rgb"] = rgb_np
        if "depth" in render_keys:
            raise NotImplementedError("This is not necessary since we'll just get the depth from collision mesh.")

            raw_depth = outputs["depth"] / self.scale
            # raise NotImplementedError("Should NOT use per-image min/max for normalization.")
            raw_depth = raw_depth.clamp(self.near_clip, self.far_clip)
            # normalized wrt near and far
            splat_depth = (raw_depth - self.near_clip) / (self.far_clip - self.near_clip)
            splat_depth = splat_depth.cpu().numpy()

            if self.fill_masks and "masks" in env_info and "render_depth" in env_info:
                # render depth is normalized 0-1 between near and far
                for group_id, (mask_in, mask_out) in env_info["masks"].items():
                    if group_id == "sky":
                        continue
                    splat_depth[mask_in] = env_info["render_depth"][..., None][mask_in]

            depth_uint8 = (splat_depth * 255).astype(np.uint8)

        return renders

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        c2w = get_camera_extrinsic_matrix(self.unwrapped.env.physics, self.camera_id, axis_correction=False)
        c2w = np.linalg.inv(self.model_tf) @ c2w

        cam_info = dict(c2w=c2w)
        cam_info["fx"] = self.fx
        cam_info["fy"] = self.fy
        cam_info["cx"] = self.width / 2
        cam_info["cy"] = self.height / 2
        cam_info["width"] = self.width
        cam_info["height"] = self.height

        info["cam_info"] = cam_info

        splat_outputs = self.splat_render(info, cam_info, *self.render_keys)
        info.update(splat_outputs)

        return obs, rew, done, info
