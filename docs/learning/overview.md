# Overview

Learning occurs in two distinct phases: Imitating expert teacher, and learning from the visual policy's own experiences with teacher
supervision.

### Phase I: Bootstrapping Off Teacher Unrolls

We collect trajectory data from the expert teacher and its intermediate checkpoints. We do not use the action labels from the sub-optimal teachers, and generate the correct action on-line during training. 

### Phase II: Learing from On-Policy Supervision

For each round, we:

1. Collect 1000 rollouts and save each timestep’s
    1. observation and action data
    2. generated image

   These are saved on luma01 server.

2. Transfer data to workstation from luma01
3. Train BC on all datasets so far using the previous checkpoint
    1. The resulting checkpoint is used to sample the next round


### Running the Experiment

We use Task queues to manage the process. Have a look at `dagger_runner.py` under `lucidsim_experiments`. It takes care of sending out the
jobs and checks when they are done. Here’s how it interacts with the three nodes you must launch:

1. The rollout jobs are sent to queue `teacher_queue_name`
    1. These are grabbed by the `flow_teacher_node.py`
    2. These are called “teacher nodes”
2. Each teacher node completes one rollout, sending RPC calls to `render_node.py` in the weaver module for the generated images
    1. The generated image is then warped to provide future frames and provide input to the sampling policy
3. Once all rollout jobs are done and gathered, the runner sends all data to the host workstation (whatever is running `dagger_runner.py`)
4. A training job is uploaded to the trainer node: `trainer.py`. This should be run on the same host workstation. Once training is complete,
   the new checkpoint is used for sampling.

The typical setup is to run `dagger_runner.py` with the appropriate arguments (specified via sweep file) on the host workstation, along with
`trainer.py`. The main runner arguments you might change will be the prompt collection and baseline interval (warping interval). See
examples of the prompt collections under `lucidsim_experiments.datasets.lucidsim_v1._collections`.

The teacher and render nodes are launched on the cluster. You may want to launch slightly more teacher nodes than render nodes, since
warping is faster and we want to keep all the renderers busy. You can monitor the speed of the teacher nodes to see whether you should
increase the number of render or teacher nodes.

An example launch file can be found in `launch_flow_teacher_node.py` and, within the weaver module, `vision_launch.py`