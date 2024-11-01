import collections
import numpy as np

from lucidsim.cfgs.ball import BallCfg
from lucidsim.utils.utils import (
    euler_from_quaternion_np,
    quat_rotate_inverse_np,
    quat_rotate_np,
    sample_camera_frustum_batch,
)
from .go1_base import Go1


class Ball(Go1):
    spawn_x_rand = 0
    spawn_y_rand = 0

    def __init__(self, sampling_period=200, stopping_distance=0.3, realsense=False, *args, **kwargs):
        """
        stopping_distance: relative to camera
        """
        super().__init__(*args, **kwargs)
        self.sampling_period = sampling_period  # 50 fps
        self.stopping_distance = stopping_distance  # meters

        self.num_samples = 0
        self.reach_goal_count = 0

        # totals: dist traveled in ball direction and total spawn distance
        self.x_displacement = 0
        self.total_sample_distance = 0

        # for current sample: furthest distance traveled in the ball direction and current spawn distance
        self.current_x_displacement = 0
        self.current_sample_distance = 0

        self.triggered_flag = False

        self.frustum_cfg = BallCfg.frustum
        if realsense:
            self.frustum_cfg = BallCfg.realsense_frustum

    def initialize_episode(self, physics):
        super().initialize_episode(physics)
        self.step_counter = -1

        self.after_step(physics)

        # reset all metrics
        self.step_counter = 0
        self.num_samples = 0
        self.reach_goal_count = 0
        self.x_displacement = 0
        self.total_sample_distance = 0

    def resample_ball(self, physics):
        x, y, z = sample_camera_frustum_batch(
            self.frustum_cfg.horizontal_fov,
            self.frustum_cfg.width,
            self.frustum_cfg.height,
            self.frustum_cfg.near,
            self.frustum_cfg.far,
            num_samples=20,
            horizontal_fov_min=self.frustum_cfg.horizontal_fov_min,
            random_state=self._random,
        )

        samples_to_cam = np.hstack([x, y, z])

        samples_to_robot = samples_to_cam + np.array(self.frustum_cfg.cam_position)
        robot_to_world_trans = physics.named.data.qpos[:3]
        w_first = physics.named.data.qpos[3:7]
        robot_to_world_rot = np.concatenate([w_first[1:], w_first[:1]])[None, ...]
        samples_to_world = quat_rotate_np(robot_to_world_rot, samples_to_robot) + robot_to_world_trans

        try:
            idx = np.where(samples_to_world[:, 2] > 0)[0][0]
        except IndexError:
            return

        return samples_to_world[idx]

    def update_goals(self, physics):
        if self.step_counter % self.sampling_period == 0:
            # this is the first physics step with the new goal
            self.total_sample_distance += self.current_sample_distance
            self.num_samples += 1
        elif (self.step_counter + 1) % self.sampling_period == 0:
            max_retries = 50
            for _ in range(max_retries):
                ball_pos = self.resample_ball(physics)
                if ball_pos is not None:
                    break
            else:
                raise NotImplementedError("What to do?")

            print("Reset to ", ball_pos, self.step_counter, self.reach_goal_count, self.num_samples)
            physics.named.data.mocap_pos["ball"] = ball_pos
            self.triggered_flag = False
            self.x_displacement += self.current_x_displacement

            self.current_sample_distance = np.linalg.norm(physics.named.data.xpos["face"][:2] - ball_pos[:2]) - self.stopping_distance
            self.current_x_displacement = 0

        # check whether goal has been reached
        ball_to_world = physics.named.data.mocap_pos["ball"]
        face_to_world = physics.named.data.xpos["face"]
        dist = np.linalg.norm(ball_to_world[:2] - face_to_world[:2])

        progress = self.current_sample_distance - (dist - self.stopping_distance)

        self.current_x_displacement = max(self.current_x_displacement, progress)
        self.current_x_displacement = min(self.current_x_displacement, self.current_sample_distance)

        # print(dist)

        if not self.triggered_flag and dist < self.stopping_distance:
            print("here")
            self.reach_goal_count += 1
            self.triggered_flag = True

    def get_observation(self, physics):
        """Returns an observation of body orientations, height and velocites."""
        obs = collections.OrderedDict()

        obs["ang_vel"] = physics.base_ang_vel * self.obs_scales.ang_vel

        w_last = physics.base_quat

        # projected_gravity = quat_rotate_inverse_np(w_last, self.gravity_vec)
        # obs["projected_gravity"] = projected_gravity

        roll, pitch, _ = euler_from_quaternion_np(w_last)
        obs["imu"] = np.array([roll, pitch, 0.0])

        ball_pos = physics.named.data.xpos["ball"]
        base_pos = physics.named.data.xpos["trunk"]

        ball_to_base = quat_rotate_inverse_np(w_last, ball_pos - base_pos)

        yaw = np.arctan2(ball_to_base[1], ball_to_base[0])

        obs["delta_yaw"] = np.array([yaw, yaw])

        speed = self.command_speed
        obs["speed"] = np.array([0.0, 0.0, speed])

        # no parkour
        obs["env_mask"] = np.array([0.0, 1.0])

        # parkour
        # obs["env_mask"] = np.array([1., 0.])

        obs["dof_pos"] = (physics.dof_pos - self.default_dof_pos) * self.obs_scales.dof_pos
        obs["dof_vel"] = physics.dof_vel * self.obs_scales.dof_vel

        obs["actions"] = self.action_buf[:]

        obs["contact"] = self.contact_filt[:] - 0.5

        # privileged obs
        obs["heightmap"] = self.heightmap_stub
        obs["priv_explicit"] = self.prev_stub
        obs["priv_latent"] = self.prev_latent_stub

        return obs

    def get_metrics(self):
        frac_goals_reached = self.reach_goal_count / self.num_samples

        x_displacement = self.x_displacement / self.total_sample_distance

        # TODO: implement metrics for X displacement

        return dict(
            frac_goals_reached=frac_goals_reached,
            x_displacement=x_displacement,
        )  # x_displacement
