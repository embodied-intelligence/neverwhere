
# Visualizing Camera Frustums

You can programmatically insert camera frustums into the scene. Here
we stress-test neverwhere by inserting 1728 frustums.

![figures/12_camera.jpg](figures/12_camera.jpg)

Simply run the following script:

```python
from neverwhere import neverwhere, neverwhereSession
from neverwhere.schemas import DefaultScene, Frustum

n, N = 12, 12 ** 3

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
                position=[i % n, (i // n) % n, (i // n ** 2) % n],
                rotation=[0.5 * 3.14, 0, 0],
            )
            for i in range(N)
        ]
    )
```
