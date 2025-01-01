import os
import tempfile
import imageio
import numpy as np
from PIL import Image
from skimage import img_as_ubyte

def save_video(frames, path, filename, fps=50):
    _, format = filename.split('.')
    try:
        imageio.v3.imwrite(os.path.join(path, filename), img_as_ubyte(frames), fps=fps)
    except imageio.core.NeedDownloadError:
        imageio.plugins.ffmpeg.download()
        imageio.v3.imwrite(os.path.join(path, filename), img_as_ubyte(frames), fps=fps)
        
def save_image(image, path, normalize=False):
    """Save an image to disk.
    
    Args:
        image: The image array to save
        path: Path where to save the image
        normalize: Whether to normalize the image values to [0,1] range
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if normalize:
        image = image.astype(float)
        image -= image.min()
        image /= image.max() + 1e-8
        image = (image * 255).astype(np.uint8)
    elif image.dtype in [np.float32, np.float64]:
        image = (image * 255).astype(np.uint8)
        
    if len(image.shape) == 3 and image.shape[-1] == 1:
        image = image[...,0]
        
    Image.fromarray(image).save(path)