from params_proto import Proto, ParamsProto


class DoctorArgs(ParamsProto):
    data_server = Proto(env="WEAVER_DATA_SERVER")
    dataset_name = "/lucidsim/lucidsim/corl/lucidsim_datasets/chase_cones_grassy_courtyard_prompts_v2"


def main():
    from ml_logger import ML_Logger

    logger = ML_Logger(root=DoctorArgs.data_server, prefix=DoctorArgs.dataset_name)

    trajectories_list = logger.glob("*trajectory.pkl")
    rollout_ids = [int(traj.split("_")[0]) for traj in trajectories_list]
    for rollout_id in rollout_ids:
        # print(f"Checking {rollout_id}")
        with logger.Prefix(f"{rollout_id}_ego_views"):
            img_types = logger.glob("*")
            lengths = []
            for img_type in img_types:
                imgs = logger.glob(f"{img_type}/*.jpeg")
                if not imgs:
                    imgs = logger.glob(f"{img_type}/*.png")
                lengths.append(len(imgs))

            # assert all([length == lengths[0] for length in lengths]), f"Lengths are not all equal!! {lengths}"

        desired_length = lengths[0]

        with logger.Prefix(f"{rollout_id}_imagen"):
            imgs = logger.glob("*.jpeg")
            img_ids = [int(img.split("_")[1].split(".")[0]) for img in imgs]
            if len(imgs) != desired_length:
                print(f"Length mismatch: {len(imgs)} != {desired_length} for {rollout_id}")
                # find which images are missing
                missing_ids = set(range(desired_length)) - set(img_ids)


if __name__ == "__main__":
    main()
