from pathlib import Path

from cmx import doc
from asyncio import sleep


async def save_doc():
    await sleep(10.0)

    result = await app.grab_render(downsample=2)
    doc.window.logger.client.log_buffer(f"../docs/_static/{Path(__file__).stem}.jpg", result.value["frame"])
    print(doc.window.logger)
    doc.flush()
    print("Example run is complete.")
    exit()


doc @ """
# Visualizing Camera Frustums

You can programmatically insert camera frustums into the scene. Here
we stress-test neverwhere by inserting 1728 frustums.
"""
doc.image(src=f"figures/{Path(__file__).stem}.jpg", width=400)

doc @ """
Simply run the following script:
"""
with doc, doc.skip:
    from neverwhere import neverwhere, neverwhereSession
    from neverwhere.schemas import DefaultScene, Frustum

    n, N = 12, 12**3

    app = neverwhere()

    @app.spawn(start=True)
    async def main(sess: neverwhereSession):
        sess.set @ DefaultScene(
            *[
                Frustum(
                    key=f"frustum-{i}",
                    scale=10,
                    showImagePlane=True,
                    showFrustum=False,
                    showFocalPlane=False,
                    position=[i % n, (i // n) % n, (i // n**2) % n],
                    rotation=[0.5 * 3.14, 0, 0],
                )
                for i in range(N)
            ]
        )

        # # fmt: off
        # await save_doc()
