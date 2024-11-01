import gym
import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Literal


class TerrainRandomizationWrapper(gym.Wrapper):
    """
    Randomizes terrains through provided rand_params (dict)
    Parameters vary depending on the terrain type.
    Randomization targets are geoms and bodies prefixed by the terrain type.
    """

    def __init__(
        self,
        env,
        terrain_type: Literal["parkour", "hurdle", "stairs", "gaps"],
        rand_params: dict,
        random=None,
        **rest,
    ):
        super().__init__(env)
        self.env = env

        self.rand_params = rand_params

        self.rng = np.random.RandomState(random)

        self.terrain_fn = getattr(self, f"set_{terrain_type}")

    def sample(self, params):
        terrain_params = {}
        for key, value in params.items():
            if key.startswith("_"):
                # discrete parameter
                terrain_params[key[1:]] = self.rng.choice(value)
            else:
                terrain_params[key] = self.rng.uniform(value[0], value[1])

        return terrain_params

    def set_parkour(self, terrain_params):
        physics = self.unwrapped.env.physics

        tilt_mul = [-1, 1, -1]
        for i, platform in enumerate(["ramp-1", "ramp-2", "ramp-3"]):
            if "tilt" in terrain_params:
                euler = [tilt_mul[i] * terrain_params["tilt"], 0, 0]
                rot = R.from_euler("XYZ", euler, degrees=False)
                w_last = rot.as_quat()
                w_first = [w_last[3], *w_last[:3]]

                physics.named.model.body_quat[platform] = w_first
            if "y_offset" in terrain_params:
                physics.named.model.body_pos[platform][1] = tilt_mul[i] * terrain_params["y_offset"]

            # Here, waypoints don't need adjusting since they are defined relative to the platforms
            # Todo: make the others consistent with this, easier to work this way
            # physics.named.model.body_pos[f"waypoint-{i}"][:2] = physics.named.model.body_pos[platform][:2]

    def set_hurdle(self, terrain_params):
        physics = self.unwrapped.env.physics

        hurdles = ["hurdle-1", "hurdle-2", "hurdle-3"]

        for i, hurdle in enumerate(hurdles):
            if "width" in terrain_params:
                physics.named.model.geom_size[hurdle][1] = terrain_params["width"]
            if "height" in terrain_params:
                physics.named.model.geom_size[hurdle][2] = terrain_params["height"]
            if "spacing" in terrain_params:
                physics.named.model.body_pos[hurdle][0] = 2 + i * terrain_params["spacing"]

            if 0 < i < len(hurdles) - 1:
                physics.named.model.body_pos[f"waypoint-{i - 1}"][:2] = np.mean(
                    [physics.named.model.body_pos[hurdle][:2], physics.named.model.body_pos[hurdles[i - 1]][:2]], axis=0
                )

    def set_stairs(self, terrain_params):
        physics = self.unwrapped.env.physics

        steps = [0, 1, 2, 1, 0]

        width = terrain_params.get("width", physics.named.model.geom_size["step-1"][1])
        height = terrain_params.get("height", physics.named.model.geom_size["step-1"][2])
        spacing = terrain_params.get("spacing", physics.named.model.body_pos["step-2"][0] - physics.named.model.body_pos["step-1"][0])

        print(width, height, spacing)

        for i, step in enumerate(["step-1", "step-2", "step-3", "step-4", "step-5"]):
            physics.named.model.geom_size[step][0] = spacing
            physics.named.model.geom_size[step][1] = width
            physics.named.model.geom_size[step][2] = height
            physics.named.model.body_pos[step][2] = steps[i] * height
            physics.named.model.body_pos[step][0] = 2 + i * spacing

        # set waypoints
        waypoint_mul = [-1, -1, 0, 1, 1]
        for i in range(5):
            physics.named.model.body_pos[f"waypoint-{i}"][0] = (
                physics.named.model.body_pos[f"step-{i + 1}"][0] + waypoint_mul[i] * spacing / 2
            )
            physics.named.model.body_pos[f"waypoint-{i}"][2] = physics.named.model.body_pos[f"step-{i + 1}"][2] + height

            print(physics.named.model.body_pos[f"waypoint-{i}"])

    def set_architecture_stairs(self, terrain_params):
        physics = self.unwrapped.env.physics

        # width = terrain_params.get("width", physics.named.model.geom_size["step-1"][1])
        height = terrain_params.get("step_height")
        length = terrain_params.get("step_length")

        print(height, length)

        for i, step in enumerate(["step-01", "step-02", "step-03", "step-04", "step-05", "step-06"]):
            physics.named.model.geom_size[step][0] = length
            # physics.named.model.geom_size[step][1] = width
            physics.named.model.geom_size[step][2] = height
            physics.named.model.body_pos[step][2] = i * height
            physics.named.model.body_pos[step][0] = 2 + i * length

        platform_size = 4
        physics.named.model.geom_size["step-06"][0] = platform_size
        physics.named.model.body_pos["step-06"][0] += platform_size

        for waypoint in ["waypoint-00", "waypoint-02", "waypoint-04", "waypoint-05"]:
            physics.named.model.body_pos[waypoint][0] = -length / 2
            physics.named.model.body_pos[waypoint][2] = height

    def set_gaps(self, terrain_params):
        physics = self.unwrapped.env.physics

        for i, gap in enumerate(["table-1", "table-2", "table-3"]):
            physics.named.model.geom_size[gap][1] = terrain_params["width"]
            physics.named.model.geom_size[gap][0] = terrain_params["length"]

            # for gaps, wayponts go right at the tables center
            physics.named.model.body_pos[f"waypoint-{i}"][:2] = physics.named.model.body_pos[gap][:2]

    def set_stairs_wh(self, terrain_params):
        physics = self.unwrapped.env.physics

        # first, set the size
        height = terrain_params.get("step_height")
        length = terrain_params.get("step_length")
        width = terrain_params.get("step_width")

        print(f"Height: {height}, Length: {length}, Width: {width}")

        geom_size = [length, width, height]

        waypoint_pos = [-length / 2, 0, height]
        right_wall_pos = [4, width, height / 2]
        left_wall_pos = [-4, width, height / 2]

        for i, step in enumerate(["step-01", "step-02", "step-03", "step-04", "step-05"]):
            physics.named.model.geom_size[step] = geom_size
            physics.named.model.body_pos[step][0] = 2 + i * length
            physics.named.model.body_pos[step][2] = i * height

        for waypoint in ["waypoint-01", "waypoint-02", "waypoint-03"]:
            physics.named.model.body_pos[waypoint] = waypoint_pos

        # platform
        size = 4

        last_step_x = physics.named.model.body_pos["step-05"][0]
        platform_pos = last_step_x + size
        physics.named.model.body_pos["step-06"][0] = platform_pos

    def reset(self):
        terrain_params = self.sample(self.rand_params)
        self.terrain_fn(terrain_params)

        obs = self.env.reset()
        return obs
