"""


from zaku import TaskQ
queue = TaskQ(name="lucidsim:eval-worker-queue-1", uri="http://escher.csail.mit.edu:8100")
queue.clear_queue()

for i in range(10):
    deps = {"$kill": True}
    queue.add(deps)

queue.clear_queue()

"""

from ml_logger.job import instr
from zaku import TaskQ

machines = [
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=0),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=1),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=2),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=3),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=0),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=1),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=2),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=3),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=0),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=1),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=2),
    dict(ip="isola-2080ti-2.csail.mit.edu", gpu_id=3),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=0),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=1),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=2),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=3),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=4),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=5),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=6),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=7),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=0),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=1),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=2),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=3),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=4),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=5),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=6),
    dict(ip="isola-v100-2.csail.mit.edu", gpu_id=7),
]

ips = {
    # "vision01": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision02": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    "vision03": [0, 1, 2, 3] * 3,
    # "vision04": [0, 1, 2, 3] * 3,
    "vision05": [0, 1, 2, 3] * 3,
    "vision06": [0, 1, 2, 3] * 3,
    # "vision07": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision09": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision09": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision10": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision11": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision12": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    "vision15": [0, 1] * 3,
    # "vision20": [1, 2, 3, 4, 5, 6] * 5,
    # "vision21": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision23": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
    # "vision24": [0, 1, 2, 3, 4, 5, 6, 7] * 3,
}

if __name__ == "__main__":
    import jaynes
    from lucidsim.traj_samplers.worker_nodes.eval_node import entrypoint

    for ip, gpus in ips.items():
        for gpu in gpus:
            host = ip
            visible_devices = f"{gpu}"

            envs = f"CUDA_VISIBLE_DEVICES={visible_devices} MUJOCO_EGL_DEVICE_ID={visible_devices}"
            jaynes.config(
                launch=dict(ip=host),
                runner=dict(
                    envs=envs,
                    # shell="screen -dm /bin/bash --norc",
                ),
            )

            thunk = instr(entrypoint, queue_name=f"{TaskQ.ZAKU_USER}:lucidsim:eval-worker-queue-1")
            jaynes.add(thunk)

        jaynes.execute()

    # jaynes.execute()
    jaynes.listen()
