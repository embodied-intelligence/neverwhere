from pprint import pformat
from warnings import warn

import os
import gym
import torch
import numpy as np
import cv2

from neverwhere.utils.depth_util import z2r
from neverwhere.utils.tf_utils import get_camera_extrinsic_matrix

def compute_ray_directions(fovy, width, height):
    """
    Compute the ray directions for a given frame using standard camera coordinates
    where +Z is forward, +Y is down, and +X is right.
    """
    # Compute field of view in radians
    fovy_rad = torch.deg2rad(torch.tensor(fovy))
    fovx_rad = 2 * torch.atan(torch.tan(fovy_rad/2) * width/height)

    # Create normalized pixel coordinates
    i, j = torch.meshgrid(
        torch.linspace(-1, 1, width),
        torch.linspace(-1, 1, height),
        indexing='xy'
    )

    # Convert to direction vectors
    z = torch.ones_like(i)  # Forward is positive z
    x = i * torch.tan(fovx_rad/2)  # Right is positive x
    y = j * torch.tan(fovy_rad/2)  # Down is positive y
    
    # Stack into direction vectors and normalize
    directions = torch.stack([x, y, z], dim=-1)
    directions = directions / torch.norm(directions, dim=-1, keepdim=True)

    return directions


class PointCloudWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        *,
        width=1280,
        height=720,
        camera_id="ego-rgb",
        lidar_camera_ids=["lidar0", "lidar1", "lidar2", "lidar3"],
        lidar_width=640,
        lidar_height=640,
        range_threshold=10,
        **rest,
    ):
        super().__init__(env)
        if rest:
            warn("received extra parameters:" + pformat(rest))
        self.env = env

        self.width = width
        self.height = height
        self.camera_id = camera_id
        self.lidar_camera_ids = lidar_camera_ids
        self.lidar_width = lidar_width
        self.lidar_height = lidar_height
        self.range_threshold = range_threshold
        
    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        
        points_list = []
        for lidar_camera_id in self.lidar_camera_ids:
            frame = self.render(
                "depth",
                width=self.lidar_width,
                height=self.lidar_height,
                camera_id=lidar_camera_id,
            )
            
            valid_mask = frame < self.range_threshold
            fovy = self.unwrapped.env.physics.named.model.cam_fovy[lidar_camera_id]
            range, *_ = z2r(frame, fov=fovy, h=self.lidar_height, w=self.lidar_width)
            
            ray_directions = compute_ray_directions(fovy, self.lidar_width, self.lidar_height)
            camera_pos = self.unwrapped.env.physics.named.data.cam_xpos[lidar_camera_id]
            camera_rot = self.unwrapped.env.physics.named.data.cam_xmat[lidar_camera_id].reshape(3, 3)
            
            points = (ray_directions * range[..., None]).numpy()
            points = (camera_rot @ points.reshape(-1, 3).T).T + camera_pos
            points = points[valid_mask.reshape(-1)]
            points_list.append(points)

        points = np.concatenate(points_list, axis=0)
        
        # export points to ply
        # colors is splat_rgb
        # ply_path = "debug/points.ply"
        # import open3d as o3d
        # pcd = o3d.geometry.PointCloud()
        # pcd.points = o3d.utility.Vector3dVector(points)
        # # pcd.colors = o3d.utility.Vector3dVector(splat_rgb.reshape(-1, 3).astype(np.float32) / 255)
        # o3d.io.write_point_cloud(ply_path, pcd)
        
        # render points from new camera
        c2w = get_camera_extrinsic_matrix(self.unwrapped.env.physics, self.camera_id, axis_correction=False)
        w2c = np.linalg.inv(c2w)
        points_cam = (w2c @ np.concatenate([points.reshape(-1, 3), np.ones((points.reshape(-1, 3).shape[0], 1))], axis=1).T).T
        points_cam = points_cam[:, :3] / points_cam[:, 3:]

        # project points to image plane
        fovy_new = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]
        f = 0.5 * self.height / np.tan(fovy_new * np.pi / 360)
        K = np.array([
            [f, 0, self.width/2],
            [0, f, self.height/2], 
            [0, 0, 1]
        ])
        points_2d = points_cam[:, :2] / points_cam[:, 2:]
        points_2d = (K[:2, :2] @ points_2d.T).T + K[:2, 2]

        valid_mask = (points_cam[:, 2] > 0) & \
                    (points_2d[:, 0] >= 0) & (points_2d[:, 0] < self.width) & \
                    (points_2d[:, 1] >= 0) & (points_2d[:, 1] < self.height)
        points_2d = points_2d[valid_mask].astype(np.int32)

        # Create depth visualization using a colormap
        depths = points_cam[valid_mask, 2]  # Get depths of valid points
        normalized_depths = (depths - depths.min()) / (depths.max() - depths.min())
        
        # Create colormap (using turbo colormap for better depth visualization)
        colors = cv2.applyColorMap((normalized_depths * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
        
        rendered_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        rendered_img[points_2d[:, 1], points_2d[:, 0]] = colors.squeeze()

        info["pointclouds"] = rendered_img
        
        # debug mode, visualize points
        # save debug visualization
        # os.makedirs("debug", exist_ok=True)
        # cv2.imwrite("debug/points.png", cv2.cvtColor(rendered_img, cv2.COLOR_RGB2BGR))
        return obs, rew, done, info
