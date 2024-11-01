import numpy as np

from lucidsim.cfgs.ball import BallCfg
from lucidsim.utils.utils import quat_rotate_np, sample_camera_frustum_batch
from .ball import Ball
from .go1_base import Go1


class Ball2(Ball):
    """
    Same as Ball, but with a distractor ball in the scene.
    """

    def resample_ball(self, physics):
        x, y, z = sample_camera_frustum_batch(
            BallCfg.frustum.horizontal_fov,
            BallCfg.frustum.width,
            BallCfg.frustum.height,
            BallCfg.frustum.near,
            BallCfg.frustum.far,
            num_samples=20,
            horizontal_fov_min=BallCfg.frustum.horizontal_fov_min,
        )
        samples_to_cam = np.hstack([x, y, z])
        samples_to_robot = samples_to_cam + np.array(BallCfg.frustum.cam_position)

        # reflect about the Y axis
        samples_to_robot_distractor = samples_to_robot * np.array([1, -1, 1])

        robot_to_world_trans = physics.named.data.xpos["trunk"]

        samples_to_world = (
            quat_rotate_np(physics.base_quat[None, ...], samples_to_robot) + robot_to_world_trans
        )

        samples_to_robot_distractor = (
            quat_rotate_np(physics.base_quat[None, ...], samples_to_robot_distractor)
            + robot_to_world_trans
        )

        try:
            idx = np.where(samples_to_world[:, 2] > 0)[0][0]
        except IndexError:
            return None, None

        return samples_to_world[idx], samples_to_robot_distractor[idx]

    def update_goals(self, physics):
        max_retries = 10
        if self.step_counter % self.sampling_period == 0:
            for _ in range(max_retries):
                ball_pos, ball_pos_distractor = self.resample_ball(physics)
                if ball_pos is not None:
                    break
            else:
                raise NotImplementedError("What to do?")

            self.triggered_flag = False
            self.num_samples += 1
            print(f"Reset to {ball_pos} and {ball_pos_distractor}")
            physics.named.data.mocap_pos["ball"] = ball_pos
            physics.named.data.mocap_pos["ball_2"] = ball_pos_distractor

        # check whether goal has been reached
        ball_to_world = physics.named.data.xpos["ball"]
        robot_to_world = physics.named.data.xpos["trunk"]

        cam_to_robot = np.array([BallCfg.frustum.cam_position])

        cam_to_world = quat_rotate_np(physics.base_quat[None, ...], cam_to_robot) + robot_to_world
        cam_to_world = cam_to_world[0]

        dist = np.linalg.norm(ball_to_world[:2] - cam_to_world[:2])
        if not self.triggered_flag and dist < self.stopping_distance:
            self.reach_goal_count += 1
            self.triggered_flag = True
