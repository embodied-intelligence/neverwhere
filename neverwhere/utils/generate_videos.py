"""
Generate videos from experiment prefix root
"""

logger_root = "http://luma01.csail.mit.edu:4000"

logger_prefix = "/scenes/chase_v3"

from ml_logger import ML_Logger

logger = ML_Logger(root=logger_root, prefix=logger_prefix)

imagens = logger.glob("**/*imagen")

for folder in imagens:
    with logger.Prefix(folder):
        files = sorted(logger.glob("*.jpeg"))

        uuid = folder.split("_")[-2].split("/")[-1]

        if len(files) == 600:
            print("good", folder)
            logger.make_video(files, f"../{uuid}.mp4", fps=50)
