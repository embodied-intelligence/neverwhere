from ml_logger import logger

from lucidsim.traj_samplers import unroll_stream

if __name__ == "__main__":
    gen = unroll_stream.main(
        env_name="Extensions-cones-stairs_bcs-lucidsim-v1",
        checkpoint="/lucid-sim/lucid-sim/baselines/launch_gains/2024-03-20/04.03.35/go1/300/20/0.5/checkpoints/model_last.pt",
        vision_key=None,
        render=True,
        num_steps=600,
        delay=0,
        stop_after_termination=False,
    )

    print(logger)
    print(logger.get_dash_url())

    for i, data in enumerate(gen):

        if i == 41:
            logger.save_image(data['midas_depth'], f"midas_depth.png")
            logger.save_image(data['foreground_mask'], f"foreground_mask.png")
            logger.save_image(data['background_mask'], f"background_mask.png")
            logger.save_image(data['ego_render'], f"ego_render.png")
            logger.save_image(data['flow_image'], f"flow_image.png")

            if 'cone_mask' in data:
                logger.save_image(data['cone_mask'], f"cone_mask.png")

        logger.save_image(data['midas_depth'], f"midas_depth/frame_{i:05d}.png")
        logger.save_image(data['foreground_mask'], f"foreground_mask/frame_{i:05d}.png")
        logger.save_image(data['background_mask'], f"background_mask/frame_{i:05d}.png")
        logger.save_image(data['ego_render'], f"ego_render/frame_{i:05d}.png")
        logger.save_image(data['flow_image'], f"flow_image/frame_{i:05d}.png")

        if 'cone_mask' in data:
            logger.save_image(data['cone_mask'], f"cone_mask/frame_{i:05d}.png")

    logger.make_video("ego_render/*.png", "ego.mp4", fps=50)
    logger.make_video("midas_depth/*.png", "depth.mp4", fps=50)
    logger.make_video("foreground_mask/*.png", "foreground.mp4", fps=50)
    logger.make_video("background_mask/*.png", "background.mp4", fps=50)
    logger.make_video("cone_mask/*.png", "cone.mp4", fps=50)
    logger.make_video('flow_image/*.png', "flow_image.mp4", fps=50)
