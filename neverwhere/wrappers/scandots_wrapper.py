import gym
import numpy as np
from typing import List

from lucidsim.utils.depth_util import invisibility
from lucidsim.utils.utils import quat_apply_yaw_np


# todo: add a config struct here.


class ScandotsWrapper(gym.Wrapper):
    def __init__(
        self,
        env,
        *,
        n_proprio: int = 53,
        # 1mx1.6m rectangle (without center line)
        xs: List[float] = np.linspace(-0.45, 1.2, 12),
        ys: List[float] = np.linspace(-0.75, 0.75, 11),
        cam_height: int = 480,
        cam_width: int = 480,
        cam_altitude: int = 25,
        camera_id: str = "heightmap",
        # prefixes
        invisible_prefix: List[str] = ["ball", "cone", "wall", "soccer", "basketball"],
        **_,
    ):
        super().__init__(env)
        self.env = env
        self.xs = xs
        self.ys = ys
        self.n_proprio = n_proprio
        self.scan_dim = len(self.xs) * len(self.ys)
        self.camera_id = camera_id
        i, j = np.meshgrid(self.xs, self.ys, indexing="ij")
        self.height_points = np.stack(
            [
                i.flatten(),
                j.flatten(),
                np.zeros(self.scan_dim),
            ],
            axis=1,
        )

        self.cam_height = cam_height
        self.cam_width = cam_width
        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[self.camera_id]

        self.cam_altitude = cam_altitude

        model = self.unwrapped.env.physics.model
        all_geom_names = [model.geom(i).name for i in range(model.ngeom)]

        self.invisible_objects = []
        for prefix in invisible_prefix:
            self.invisible_objects.extend([geom_name for geom_name in all_geom_names if geom_name.startswith(prefix)])

        self.px_scale = self.get_px_scale(
            width=self.cam_width,
            height=self.cam_height,
            fovy=self.fovy,
            altitude=self.cam_altitude,
        )

    def get_px_scale(self, *, width, height, fovy, altitude):
        """
        Get the pixels per meter scale for the heightmap.
        """

        cam_x_dist = altitude * np.tan(np.deg2rad(fovy / 2))
        cam_y_dist = cam_x_dist * width / height

        # scale: pixels per meter
        px_scale = height / (2 * cam_x_dist)

        # make sure the range is enough
        assert (
            max(self.xs) < cam_x_dist and max(self.ys) < cam_y_dist
        ), "heightmap camera does not cover sufficient range. Try increasing cam_altitude or fovy"

        return px_scale

    def get_idxs(self, *, px_scale, base_quat):
        """Get the pixel indices for the measured points, accounting for yaw.

        base_quat: w last
        """
        rotated_points = quat_apply_yaw_np(base_quat, self.height_points)

        rotated_points_px = (rotated_points[:, :2] * px_scale).astype(np.int32)

        return rotated_points_px

    def step(self, action):
        obs, rew, done, info = self.env.step(action)

        with invisibility(self.unwrapped.env.physics, self.invisible_objects):
            # remove the ball and cone from the heightmap, if it exists
            info["heightmap"] = self.render(
                "depth",
                width=self.cam_width,
                height=self.cam_height,
                camera_id=self.camera_id,
            )

        centered_px = self.get_idxs(px_scale=self.px_scale, base_quat=self.unwrapped.env.physics.base_quat)
        px = -centered_px[:, 0] + self.cam_height // 2
        py = -centered_px[:, 1] + self.cam_width // 2

        # clip within bounds
        px = np.clip(px, 0, self.cam_height - 1)
        py = np.clip(py, 0, self.cam_width - 1)

        # samples dist from the base
        heightsamples = info["heightmap"][px, py] - self.cam_altitude
        heightsamples = np.clip(heightsamples - 0.3, -1, 1)

        heightsamples_img = heightsamples.reshape(len(self.xs), -1).T
        heightsamples_img = np.rot90(heightsamples_img, -1)
        heightsamples_img = np.flipud(heightsamples_img)

        info["height_samples"] = heightsamples_img

        obs[:, self.n_proprio : self.n_proprio + self.scan_dim] = heightsamples

        return obs, rew, done, info
