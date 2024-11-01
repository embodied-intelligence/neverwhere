from params_proto import PrefixProto
from typing import Literal


class BallCfg(PrefixProto, cli=False):
    # todo: deprecate this.
    class frustum:
        cam_position = [0.27, 0, 0.015]
        width = 640
        height = 180
        horizontal_fov_min = 50
        horizontal_fov = 90
        near = 0.5
        far = 1.25

    class realsense_frustum:
        cam_position = [0.27, 0, 0.015]
        width = 640
        height = 180
        horizontal_fov_min = 35
        horizontal_fov = 65
        near = 0.5
        far = 1.25

    # todo: deprecate this.
    class vision(PrefixProto, cli=False):
        width = 80
        height = 45

        # applies only on depth render type
        near_clip = 0.05
        far_clip = 2.0

        normalize_depth = True
        render_type: Literal["depth", "rgb"] = "rgb"

        compute_deltas = False
        drop_last = False
        stack_size = 1

        imagenet_pipe = True
