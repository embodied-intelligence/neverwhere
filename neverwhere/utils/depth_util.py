from asyncio import sleep

import numpy as np
from contextlib import contextmanager


def z2r(z, fov, *, h, w):
    """
    Convert metric depth to range map

    :param z: metric depth, in Size(H, W)
    :param fov: verticle field of view
    :param h: height of the image
    :param w: width of the image
    """
    f = h / 2 / np.tan(fov / 2)
    x = (np.arange(w) - w / 2) / f
    y = (np.arange(h) - h / 2) / f
    xs, ys = np.meshgrid(x, y, indexing="xy")

    d = z * np.sqrt(1 + xs ** 2 + ys ** 2)

    return d, xs, ys


def r2z(r, fov, h, w):
    """Convert range map to metric depth.

    :param r: range map, in Size(H, W)
    :param fov: verticle field of view
    :param h: height of the image
    :param w: width of the image
    """
    f = h / 2 / np.tan(fov / 2)
    x = (np.arange(w) - w / 2) / f
    y = (np.arange(h) - h / 2) / f
    xs, ys = np.meshgrid(x, y, indexing="xy")

    r_scale = np.sqrt(1 + xs ** 2 + ys ** 2)
    z = r / r_scale
    return z, xs, ys


@contextmanager
def invisibility(physics, geom_names: list):
    try:
        # Check if the geom exists
        original_rgbas = []
        for geom_name in geom_names:
            original_rgba = physics.named.model.geom_rgba[geom_name].copy()
            # Set RGBA to fully transparent to hide the geom
            physics.named.model.geom_rgba[geom_name] = [0, 0, 0, 0]
            original_rgbas.append(original_rgba)

        geom_exists = True
    except KeyError:
        # Handle the case where the geom does not exist
        # print(f"Geom '{geom_name}' does not exist in the model.")
        geom_exists = False

    try:
        yield
    finally:
        if geom_exists:
            # Restore original RGBA color if the geom existed
            for geom_name, original_rgba in zip(geom_names, original_rgbas):
                physics.named.model.geom_rgba[geom_name] = original_rgba


if __name__ == "__main__":
    # this is the z depth
    z = np.ones((45, 80)) * 1

    r, xs, ys = z2r(z, np.deg2rad(70), h=45, w=80)

    from vuer import Vuer, VuerSession
    from vuer.schemas import PointCloud

    app = Vuer()


    @app.spawn(start=True)
    async def main(sess: VuerSession):

        vertices = np.stack([xs.flatten(), ys.flatten(), z.flatten()])
        sess.upsert @ PointCloud(vertices=vertices.T, key="alan pointcloud")

        vertices = np.stack([xs.flatten(), ys.flatten(), r.flatten()])
        sess.upsert @ PointCloud(vertices=vertices.T, key="range r", color="yellow")

        z_recovered, *_ = r2z(r, np.deg2rad(70), h=45, w=80)
        vert_recovered = np.stack([xs.flatten(), ys.flatten(), z_recovered.flatten()])

        sess.upsert @ PointCloud(vertices=vert_recovered.T[:1800] + [0, 0, -0.1], key="recovered pointcloud",
                                 color="red")

        while True:
            await sleep(1.0)
