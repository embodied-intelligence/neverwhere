# Heightmap Wrapper

The extreme-parkour policy requires a terrain heightmap. The way IsaacGym requires the global heightmap as input, whereas we prefer to define scene geometry via 3D primitives. So in Neverwhere, we emulate the heightmap using a downward looking camera positioned far away from the robot. This approximation is not identical to the heightmap used in the original environment, and can suffer from distortions due to the finite focal distance of this camera. 

Trying to get IsaacGym to do the same will slow down the simulation, as it will have to render heightmap on the fly.

**Data Format**