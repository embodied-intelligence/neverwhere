from cmx import doc

doc @ """
# Plane Primitive

This example shows you how to construct a plane and have it visible on both sides.

We pass in `Plane.material.side=2` to the `Plane` constructor to make it visible on both sides.

"""

with doc, doc.skip:
    from asyncio import sleep

    from neverwhere import neverwhere
    from neverwhere.events import Set
    from neverwhere.schemas import DefaultScene, Plane

    app = neverwhere()

    # use `start=True` to start the app immediately
    @app.spawn(start=True)
    async def main(session):
        session @ Set(
            DefaultScene(
                Plane(material=dict(side=2)),
            ),
        )

        while True:
            await sleep(1.0)


doc.flush()
