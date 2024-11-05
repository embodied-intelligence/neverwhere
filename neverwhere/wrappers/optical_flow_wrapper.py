import gym
import numpy as np
import re
import torch
from torchvision.utils import flow_to_image

from neverwhere.utils.depth_util import invisibility
from neverwhere.utils.tf_utils import get_camera_extrinsic_matrix, get_camera_intrinsic_matrix
from optical_flow import warp_forward


class OpticalFlowWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        *,
        width: int = 1280,
        height: int = 768,
        visualize: bool = False,  # """Visualize the flow, return in info['flow_image']."""
        camera_id: str = "ego-rgb-render",
        device: str = "cuda",
        ignored_geoms=[],  # "ball*", "soccer*", "basketball*"],
        **_,
    ):
        super().__init__(env)
        self.env = env
        self.width = width
        self.height = height
        self.camera_id = camera_id
        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]
        self.visualize = visualize

        self.device = device

        # setup sampling vars
        self.prev_depth = torch.zeros((self.height, self.width, 1), device=device)
        self.samples_to_prev = torch.zeros((self.height, self.width, 3), device=device)
        self.prev_T = torch.eye(4, device=device, dtype=torch.float64)

        self.f_px = self.height / 2 / np.tan(np.deg2rad(self.fovy) / 2)

        self.cx = self.width / 2
        self.cy = self.height / 2

        # put at center of each pixel
        us = torch.arange(self.width, device=device) + 0.5
        vs = torch.arange(self.height, device=device) + 0.5

        self.us, self.vs = torch.meshgrid(us, vs, indexing="xy")

        self.us.to(device=device)
        self.vs.to(device=device)

        self.K = torch.from_numpy(
            get_camera_intrinsic_matrix(
                self.unwrapped.env.physics,
                self.camera_id,
                self.height,
                self.width,
                self.fovy,
            ),
        ).to(device=device)

        self.ignored_geom_names = []

        model = self.unwrapped.env.physics.model

        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]

        for geom_name in all_geom_names:
            for pattern in ignored_geoms:
                compiled_pattern = re.compile(pattern)
                if compiled_pattern.match(geom_name):
                    self.ignored_geom_names.append(geom_name)
                    break

    def sample_camera(self, frame):
        """
        Samples a point centered at each pixel in the frame (Z-depth)

        Returns a tensor of shape (height, width, 3) containing the 3d coordinates of the sampled points.
        """
        xs = frame * (self.us - self.cx) / self.f_px
        ys = frame * (self.vs - self.cy) / self.f_px

        xyz = torch.stack([xs, ys, frame], axis=-1)

        return xyz

    def compute_flow(self, samples_to_prev):
        """
        Computes the optical flow between the previous frame and the new frame.
        """

        T_new_to_world = get_camera_extrinsic_matrix(self.unwrapped.env.physics, self.camera_id)
        T_new_to_world = torch.from_numpy(T_new_to_world).to(device=self.device)

        T_old_to_new = torch.linalg.inv(T_new_to_world) @ self.prev_T

        samples_to_prev_h = torch.cat([samples_to_prev, torch.ones((self.height, self.width, 1), device=self.device)], axis=-1).reshape(
            -1, 4
        )

        samples_to_current = samples_to_prev_h @ T_old_to_new.T

        # project onto the current frame
        samples_to_current_px = samples_to_current[..., :3] @ self.K.T

        samples_to_current_px = samples_to_current_px / samples_to_current_px[..., 2:]
        samples_to_current_px = samples_to_current_px.reshape(self.height, self.width, 3)

        dxs = samples_to_current_px[..., 0] - self.us
        dys = samples_to_current_px[..., 1] - self.vs

        flow = torch.stack([dxs, dys], axis=-1)

        return flow, T_new_to_world

    def compute_flow_reverse(self, current_frame):
        """ """
        current_samples = self.sample_camera(current_frame)

        T_current_to_world = get_camera_extrinsic_matrix(self.unwrapped.env.physics, self.camera_id)
        T_current_to_world = torch.from_numpy(T_current_to_world).to(device=self.device)

        T_old_to_new = torch.linalg.inv(T_current_to_world) @ self.prev_T

        current_samples_h = torch.cat(
            [current_samples, torch.ones((self.height, self.width, 1), dtype=torch.float64, device=self.device)], axis=-1
        ).reshape(-1, 4)

        samples_to_prev = current_samples_h @ torch.linalg.inv(T_old_to_new).T

        samples_to_prev_px = samples_to_prev[..., :3] @ self.K.T

        samples_to_prev_px = samples_to_prev_px / samples_to_prev_px[..., 2:]
        samples_to_prev_px = samples_to_prev_px.reshape(self.height, self.width, 3)

        dxs = samples_to_prev_px[..., 0] - self.us
        dys = samples_to_prev_px[..., 1] - self.vs

        flow = torch.stack([dxs, dys], axis=-1)

        # occlusion checking
        # depth_t = torch.from_numpy(self.prev_depth).permute(2, 0, 1)
        depth_t = self.prev_depth.permute(2, 0, 1)
        depth_t = depth_t[None, ...].float()

        # flow_t = torch.from_numpy(flow).permute(2, 0, 1)
        flow_t = flow.permute(2, 0, 1)
        flow_t = flow_t[None, ...].float()

        warped_depth = warp_forward(depth_t, -flow_t)
        warped_depth = warped_depth[0, 0]
        invalid_mask = abs(warped_depth - current_frame) > 0.4

        invalid_mask = torch.logical_and(invalid_mask, self.prev_depth[..., 0] < 5)

        return flow, invalid_mask, T_current_to_world

    def step(self, action, update_baseline=True):
        obs, rew, done, info = self.env.step(action)

        # let it do on its own, by using the provided camera id
        physics = self.unwrapped.env.physics
        # fixme: fix the ball transform
        with invisibility(physics, self.ignored_geom_names):
            frame = self.render(
                "depth",
                width=self.width,
                height=self.height,
                camera_id=self.camera_id,
            ).copy()

        frame = torch.from_numpy(frame).to(device=self.device)
        # replace > 15 (sky) with inf
        frame = torch.where(frame > 15, torch.tensor(1_000.0, device=self.device), frame)

        flow, invalid_mask, prev_T = self.compute_flow_reverse(frame)
        # flow, invalid_mask, prev_T = self.compute_flow(frame)
        prev_depth = frame[..., None]

        if update_baseline:
            self.prev_T = prev_T
            self.prev_depth = prev_depth

        # replace nan with 0
        flow = flow.cpu().numpy()
        flow_tensor = torch.from_numpy(flow).float().permute(2, 0, 1)
        flow_visualization = flow_to_image(flow_tensor).permute(1, 2, 0).numpy()

        info["flow"] = flow
        info["flow_image"] = flow_visualization
        info["flow_mask"] = invalid_mask

        return obs, rew, done, info
