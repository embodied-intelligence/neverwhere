# Optical Flow Wrapper

The Optical Flow Wrapper computes the ground-truth optical flow between two camera poses, using the scene geometry. The 


**Data Format**: The optical flow is a 2D array of shape `(H, W, 2)`, where `H` and `W` are the height and width of the image, respectively. The last dimension has two channels, representing the x and y components of the flow.

...