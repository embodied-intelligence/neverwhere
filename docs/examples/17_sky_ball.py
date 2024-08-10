from cmx import doc

doc @ """
# Showing 360 Views with a Sky Ball

This example requires a equirectangular image (shown below), which is then
mapped to a sphere as a texture. 

![equirectangular image](figures/farm_house.jpg)

Place the `[farm_house.jpg](figures/farm_house.jpg)` in the path pointed to
by the `static_root` argument of the `neverwhere` class. The neverwhere front end will
try to load from the url `http://localhost:8012/static/farm_house.jpg`.

Here is the expected result:
![marker light](figures/17_sky_ball.png)
"""
with doc, doc.skip:
    from asyncio import sleep
    import numpy as np

    from neverwhere import neverwhere, neverwhereSession
    from neverwhere.schemas import DefaultScene, Arrow, Sphere

    app = neverwhere(static_root="figures")

    n = 10
    N = 1000

    sphere = Sphere(
        args=[1, 32, 32],
        materialType="standard",
        material={"map": "http://localhost:8012/static/farm_house.jpg", "side": 1},
        position=[0, 0, 0],
        rotation=[0.5 * np.pi, 0, 0],
    )


    @app.spawn(start=True)
    async def main(proxy: neverwhereSession):
        proxy.set @ DefaultScene(sphere)

        # keep the main session alive.
        while True:
            await sleep(10)

doc.flush()
