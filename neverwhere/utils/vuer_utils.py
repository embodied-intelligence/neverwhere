from vuer.schemas import Urdf, group


def Go1(src, joints, position=(0, 0, 0), global_rotation=(0, 0, 0), key="go1", **kwargs):
    """

    Args:
        src: path to URDF (e.g.  "http://localhost:8013/static/urdf/go1.urdf")
        joints: dictionary from joint names to angles (rad)
        position: in world coordinates
        global_rotation: in rad
        **kwargs:

    Returns: Urdf schema

    """
    r, p, y = global_rotation
    return group(
        group(
            group(
                group(Urdf(src=src, jointValues=joints, key="robot", **kwargs), rotation=[r, 0, 0], key="roll"),
                rotation=[0, p, 0], key="pitch"
            ),
            rotation=[0, 0, y],
            position=position,
            key="yaw",
        ), key=key)
