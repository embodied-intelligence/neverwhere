import collections

import numpy as np
from dm_control import mujoco
from dm_control.suite import base

from neverwhere.cfgs.parkour import Go1ParkourCfg
from neverwhere.utils.utils import (
    quat_from_euler_xyz_np,
    euler_from_quaternion_np,
    get_geom_speed,
    smart_delta_yaw,
    quat_rotate_inverse_np,
)


class Physics(mujoco.Physics):
    """Physics simulation with additional features for the Go1 domain."""

    # unitree indexing
    JOINT_NAMES = [
        "FR_hip_joint",
        "FR_thigh_joint",
        "FR_calf_joint",
        "FL_hip_joint",
        "FL_thigh_joint",
        "FL_calf_joint",
        "RR_hip_joint",
        "RR_thigh_joint",
        "RR_calf_joint",
        "RL_hip_joint",
        "RL_thigh_joint",
        "RL_calf_joint",
    ]

    FOOT_NAMES = ["FR", "FL", "RR", "RL"]

    TERMINATION_CONTACT_NAMES = ["face", "base"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geom_ids = {}
        for foot_name in self.FOOT_NAMES + self.TERMINATION_CONTACT_NAMES:
            geom_id = self.data.ptr.geom(foot_name).id
            self.geom_ids[geom_id] = foot_name

    @property
    def dof_pos(self) -> np.ndarray:
        dof_positions = []
        for joint in self.JOINT_NAMES:
            dof_positions.append(self.named.data.qpos[joint])

        return np.array(dof_positions).T

    @property
    def dof_vel(self) -> np.ndarray:
        dof_velocities = []
        for joint in self.JOINT_NAMES:
            dof_velocities.append(self.named.data.qvel[joint])

        return np.array(dof_velocities).T

    @property
    def dof_states(self) -> np.ndarray:
        return np.concatenate([self.dof_pos, self.dof_vel], axis=1)

    @property
    def base_quat(self):
        """
        Returns the orientation of the base.
        Note: XYZW
        """
        w_first = self.named.data.xquat["trunk"]
        w_last = np.concatenate([w_first[1:], w_first[:1]])
        return w_last

    @property
    def base_ang_vel(self):
        """
        Returns the angular velocity of the base.
        """
        return quat_rotate_inverse_np(self.base_quat, get_geom_speed(self.model.ptr, self.data.ptr, "base"))

    @property
    def contact_filt(self):
        """
        Contact filter (4d).
        Order in untree, so FR, FL, RR, RL
        """
        contact_buf = np.zeros(4, dtype=bool)

        contacts = self._get_contacts()

        for foot in self.FOOT_NAMES:
            contact_buf[self.FOOT_NAMES.index(foot)] = np.linalg.norm(contacts[foot]) > 2.0  # 2.0

        return contact_buf

    def _get_contacts(self):
        contact_forces = {k: np.zeros(3) for k in self.geom_ids.values()}
        force_buf = np.zeros(6, dtype=np.float64)
        for i in range(len(self.data.ptr.contact)):
            contact = self.data.ptr.contact[i]

            geom1_id = contact.geom1
            geom2_id = contact.geom2

            geom1_name = self.geom_ids.get(geom1_id, None)
            geom2_name = self.geom_ids.get(geom2_id, None)

            if geom1_name is None and geom2_name is None:
                continue

            mujoco.mj_contactForce(self.model.ptr, self.data.ptr, i, force_buf)

            if geom1_name in contact_forces:
                contact_forces[geom1_name] += force_buf[:3]
            if geom2_name in contact_forces:
                contact_forces[geom2_name] += force_buf[:3]

        # Warning: this is in ZYX or something
        # print("Contact forces", contact_forces)
        return contact_forces

    def torso_upright(self):
        """Returns projection from z-axes of torso to the z-axes of world."""
        return self.named.data.xmat["torso", "zz"]

    def torso_height(self):
        """Returns the height of the torso."""
        return self.named.data.xpos["torso", "z"]

    def horizontal_velocity(self):
        """Returns the horizontal velocity of the center-of-mass."""
        return self.named.data.sensordata["torso_subtreelinvel"][0]

    def orientations(self):
        """Returns planar orientations of all bodies."""
        return self.named.data.xmat[1:, ["xx", "xz"]].ravel()


class Go1(base.Task):
    """A planar walker task."""

    # this should really be passed in.
    obs_scales = Go1ParkourCfg.obs_scales
    init_state = Go1ParkourCfg.init_state

    num_actions = 12

    n_scan = 132
    n_priv = 3 + 3 + 3
    n_priv_latent = 4 + 1 + 12 + 12
    control_dt = 0.02

    reach_goal_threshold = 0.3
    reach_goal_delay = 0.1

    spawn_x_rand = 0.5
    spawn_y_rand = 0.5
    spawn_yaw_rand = np.pi / 4

    def __init__(
        self,
        move_speed_range,
        vision=False,
        random=None,
        waypoint_prefix="waypoint",
        y_noise=0,
        x_noise=0,
        spawn_x_rand=0.5,
        spawn_y_rand=0.5,
        spawn_yaw_rand=np.pi / 4,
        # special one, if set will ignore randomization and spawn at this pose
        # _spawn_pose=None,
        initial_state=None,
        **kwargs,
    ):
        """Initializes an instance of `PlanarWalker`.

        Args:
          move_speed_range: A tuple of floats. If this value is zero, reward is given simply for
            standing up. Otherwise this specifies a target horizontal velocity for
            the walking task.
          random: Optional, either a `numpy.random.RandomState` instance, an
            integer seed for creating a new `RandomState`, or None to select a seed
            automatically (default).
        """

        if random is not None:
            random = np.random.RandomState(random)

        super().__init__(random=random)

        self._move_speed_range = move_speed_range
        self.spawn_yaw_rand = spawn_yaw_rand
        self.spawn_x_rand = spawn_x_rand
        self.spawn_y_rand = spawn_y_rand

        # self._spawn_pose = _spawn_pose
        self._initial_state = initial_state

        self._vision = vision

        self.gravity_vec = np.array([0.0, 0.0, -1.0])

        default_dof_pos = []

        for joint in Physics.JOINT_NAMES:
            default_dof_pos.append(self.init_state.default_joint_angles[joint])
        self.default_dof_pos = np.array(default_dof_pos, dtype=np.float32)

        self.resample_commands()
        self.step_counter = 0
        self.reach_goal_timer = 0

        self.current_goal_num = 0
        self.num_goals_complete = 0
        self.x_displacement = 0  # for metrics; how far toward the goal; updated every step

        self.waypoint_prefix = waypoint_prefix
        self.waypoint_y_noise = y_noise
        self.waypoint_x_noise = x_noise

        self.goal_names = None
        self.last_goal_x = None

        self.heightmap_stub = np.zeros(self.n_scan)
        self.prev_stub = np.zeros(self.n_priv)
        self.prev_latent_stub = np.zeros(self.n_priv_latent)

        self.last_contacts = np.zeros(4, dtype=bool)
        self.contact_filt = np.zeros(4, dtype=bool)
        self.action_buf = np.zeros(self.num_actions, dtype=float)

    def initialize_episode(self, physics):
        self.goal_names, self.last_goal_x = self.init_goals(physics)

        # if self._spawn_pose is not None:
        if self._initial_state is not None:
            # pick the goal index which is closest to the spawn point
            # spawn_x, spawn_y, spawn_z, spawn_yaw = self._spawn_pose
            # min_goal_x = spawn_x + 0.25

            initial_state = np.array(self._initial_state)
            min_goal_x = self._initial_state[0] + 0.25

            dists = [physics.named.data.xpos[goal_name][0] - min_goal_x for goal_name in self.goal_names]
            valid_dists = [d for d in dists if d >= 0]
            if len(valid_dists) == 0:
                first_goal_idx = -1
            else:
                print(dists)
                first_goal_idx = dists.index(min(valid_dists))

            print("First goal idx", first_goal_idx, "of", len(self.goal_names))

            self.goal_names = self.goal_names[first_goal_idx:]

            # physics.named.data.qpos[:3] += np.array([spawn_x, spawn_y, 0.0])
            # physics.named.data.qpos[2] = spawn_z

            # w_last = quat_from_euler_xyz_np(0, 0, spawn_yaw)
            # w_first = np.concatenate([w_last[3:], w_last[:3]])
            # physics.named.data.qpos[3:7] = w_first
            # physics.named.data.qpos[7:] = self.default_dof_pos

            physics.set_state(initial_state)
            return

        spawn_x = self._random.uniform(-self.spawn_x_rand, self.spawn_x_rand)
        spawn_y = self._random.uniform(-self.spawn_y_rand, self.spawn_y_rand)

        physics.named.data.qpos[:3] += np.array([spawn_x, spawn_y, 0.0])

        init_euler = [0, 0, self._random.uniform(-self.spawn_yaw_rand, self.spawn_yaw_rand)]
        w_last = quat_from_euler_xyz_np(*init_euler)
        w_first = np.concatenate([w_last[3:], w_last[:3]])
        physics.named.data.qpos[3:7] = w_first

        # set default joints
        physics.named.data.qpos[7:] = self.default_dof_pos

    def before_step(self, action: np.ndarray, physics):
        prev_action = self.action_buf[:]

        raw_action = action.copy()
        self.action_buf[:] = raw_action.copy()

        raw_action = prev_action
        clip_value = Go1ParkourCfg.control.clip_actions / Go1ParkourCfg.control.action_scale
        raw_action = np.clip(raw_action, -clip_value, clip_value)
        raw_action = raw_action * Go1ParkourCfg.control.action_scale
        raw_action += self.default_dof_pos

        super().before_step(raw_action, physics)
        # store the action in buffer
        self.action_buf[:] = action

    def after_step(self, physics):
        super().after_step(physics)

        current_contact = physics.contact_filt

        # update the contact filter by loring with previous contact
        self.contact_filt = np.logical_or(current_contact, self.last_contacts)

        # update prev contact buffer
        self.last_contacts = current_contact[:]

        self.update_goals(physics)

        self.step_counter += 1

    def init_goals(self, physics, randomize=True):
        goal_names = []
        all_body_names = [physics.model.body(i).name for i in range(physics.model.nbody)]

        for body_name in all_body_names:
            if body_name.startswith(self.waypoint_prefix):
                goal_names.append(body_name)

        goal_names = sorted(goal_names)

        if len(goal_names) == 0:
            print("Warning: no goals found!")
            return None, None

        if randomize:
            for goal in goal_names:
                y_rand = self._random.uniform(-self.waypoint_y_noise, self.waypoint_y_noise)
                x_rand = self._random.uniform(-self.waypoint_x_noise, self.waypoint_x_noise)

                # NOTE! This is the local body position, intentionally.
                # E.g. for parkour, we want to adjust relative to the tilt
                new_pos = physics.named.model.body_pos[goal].copy()
                new_pos[0] += x_rand
                new_pos[1] += y_rand

                physics.named.model.body_pos[goal] = new_pos

        last_goal_x = physics.named.data.xpos[goal_names[-1]][0]

        return goal_names, last_goal_x

    def update_goals(self, physics):
        if self.goal_names is None:
            return

        if self.reach_goal_timer > self.reach_goal_delay / self.control_dt:
            self.current_goal_num = np.clip(self.current_goal_num + 1, 0, len(self.goal_names) - 1)
            self.num_goals_complete = np.clip(self.num_goals_complete + 1, 0, len(self.goal_names))
            self.reach_goal_timer = 0

        current_goal_name = self.goal_names[self.current_goal_num]

        if (
            np.linalg.norm(physics.named.data.xpos[current_goal_name][:2] - physics.named.data.xpos["trunk"][:2])
            < self.reach_goal_threshold
        ):
            self.reach_goal_timer += 1

        x_displacement = physics.named.data.xpos["trunk"][0] / self.last_goal_x
        x_displacement = max(x_displacement, self.x_displacement)
        self.x_displacement = min(x_displacement, 1.0)

    def get_observation(self, physics):
        """Returns an observation of body orientations, height and velocites."""
        obs = collections.OrderedDict()

        obs["ang_vel"] = physics.base_ang_vel * self.obs_scales.ang_vel

        w_last = physics.base_quat

        # projected_gravity = quat_rotate_inverse_np(w_last, self.gravity_vec)
        # obs["projected_gravity"] = projected_gravity

        roll, pitch, yaw = euler_from_quaternion_np(w_last)
        obs["imu"] = np.array([roll, pitch, 0])

        if self.goal_names is not None:
            goal_name = self.goal_names[self.current_goal_num]
            waypoint_pos = physics.named.data.xpos[goal_name]
            target_pos_rel = waypoint_pos - physics.named.data.xpos["trunk"]
            target_vec_norm = target_pos_rel / np.linalg.norm(target_pos_rel)
            target_yaw = np.arctan2(target_vec_norm[1], target_vec_norm[0])

            yaw_cmd = smart_delta_yaw(yaw, target_yaw)
        else:
            yaw_cmd = 0.0

        obs["delta_yaw"] = np.array([yaw_cmd, yaw_cmd])

        speed = self.command_speed
        obs["speed"] = np.array([0.0, 0.0, speed])

        # no parkour
        # obs["env_mask"] = np.array([0., 1.])

        # parkour
        obs["env_mask"] = np.array([1.0, 0.0])

        obs["dof_pos"] = (physics.dof_pos - self.default_dof_pos) * self.obs_scales.dof_pos
        obs["dof_vel"] = physics.dof_vel * self.obs_scales.dof_vel

        obs["actions"] = self.action_buf[:]

        obs["contact"] = self.contact_filt[:] - 0.5

        # privileged obs
        obs["heightmap"] = self.heightmap_stub
        obs["priv_explicit"] = self.prev_stub
        obs["priv_latent"] = self.prev_latent_stub

        return obs

    def get_reward(self, physics):
        """Returns a reward to the agent."""
        return 0

    def resample_commands(self):
        self.command_speed = self._random.uniform(*self._move_speed_range)
        print("Command speed", self.command_speed)

    def get_metrics(self):
        return dict(
            frac_goals_reached=(self.num_goals_complete) / len(self.goal_names),
            x_displacement=self.x_displacement,
        )
