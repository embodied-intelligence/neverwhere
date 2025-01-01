import gym
import json
import numpy as np
import os
import torch

from neverwhere.gsplat.dn_model import Model
from neverwhere.utils.tf_utils import get_camera_extrinsic_matrix

DATASET_ROOT = os.environ.get("NEVERWHERE_EVAL_DATASETS")


def load_mesh_info(dataset_root, dataset_prefix):
    print("loading mesh info...")

    # extract scale and transform from data_transforms.json
    dataparser_tf_path = f"{dataset_root}/{dataset_prefix}/3dgs/data_transforms.json"
    if not os.path.exists(dataparser_tf_path):
        print("the transformation is already aligned, skipped alignment")
        return 1.0, np.eye(4)

    with open(dataparser_tf_path) as f:
        data = json.load(f)
        scale = data["scale"]
        transform = np.array(data["transform"])
        # Extend to 4x4 matrix
        tf_matrix = np.eye(4)
        tf_matrix[:3, :4] = transform

    print("mesh information is loaded!")
    return scale, tf_matrix


def load_model(dataset_root, dataset_prefix, device):
    model = Model(device=device)

    print("loading model...")
    state_dict = torch.load(f"{dataset_root}/{dataset_prefix}/3dgs/model.pt", map_location=device)
    model.load_state_dict_gsplat(state_dict, strict=False)
    model.eval()

    scale, transform = load_mesh_info(dataset_root, dataset_prefix)

    return model, scale, transform


class GSplatWrapper(gym.Wrapper):
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

        mesh_translation = self.unwrapped.env.physics.named.data.xpos["mesh"]
        mesh_rot = self.unwrapped.env.physics.named.data.xmat["mesh"].reshape(3, 3)
        mesh_scale = self.unwrapped.env.physics.named.model.mesh_scale["visual_mesh"]
        
        # mesh_tf: mesh's transformation matrix
        # first apply scale, then transform
        mesh_tf = np.eye(4)
        scale_mat = np.diag([mesh_scale[0], mesh_scale[1], mesh_scale[2], 1])
        mesh_tf[:3, :3] = mesh_rot @ scale_mat[:3, :3]
        mesh_tf[:3, 3] = mesh_translation

        # self.scale: dataparser scale
        self.model, self.scale, self.transform = load_model(DATASET_ROOT, dataset_name, device)
        
        # transformation has already included the scale
        # scale_mat = np.diag([1 / self.scale, 1 / self.scale, 1 / self.scale, 1])
        
        # splat_tf: splat to mesh
        splat_tf = self.transform
        
        # splat to mujoco
        self.model_tf = mesh_tf @ np.linalg.inv(splat_tf)

    def get_tf_info(self):
        """returns the model transformation information"""
        return {
            "model_scale": self.scale,
            "model_matrix": self.model_tf.tolist(),
            "transform_matrix": self.transform.tolist()
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
