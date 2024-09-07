<h1 class="full-width" style="font-size: 49px"><code style="font-size: 1.3em; background-clip: text; color: transparent; background-image: linear-gradient(to right, rgb(169 178 177), rgb(34 51 52), rgb(202 204 200));">Neverwhere</code> <span style="font-size: 0.3em; margin-left: -0.5em; margin-right:-0.4em;">｣</span> Benchmark Suite</h1>

<link rel="stylesheet" href="_static/title_resize.css">

Neverwhere is a photo-realistic benchmark suite for testing legged agility in quadruped robots. It is designed to offer realistic visual
observations that matches the physical world in complexity and detail.

```shell
pip install 'neverwhere[all]=={VERSION}'
```

### How to use this documentation

### Setting up Asset Files

### Running the Benchmark

- take a look at the basic tutorial or the tutorial for robotics:
    - [neverwhere Basics](environments/wrappers)
    - [Tutorial for Roboticists](environments/robotics)
- or try to take a look at the example gallery [here](examples/01_trimesh)

For comprehensive documentation on the python API, please refer to
the [API documentation | neverwhere](https://neverwhere.readthedocs.com/en/latest/api/neverwhere.html).

<!-- prettier-ignore-start -->

```{eval-rst}
.. toctree::
   :hidden:
   :maxdepth: 1
   :titlesonly:

   Quick Start <quick_start>
   Report Issues <https://github.com/neverwhere-ai/neverwhere/issues?q=is:issue+is:closed>
   CHANGE LOG <CHANGE_LOG.md>
   
.. toctree::
   :maxdepth: 3
   :caption: Environments 
   :hidden:
   
   environments/catalogue.md
   environments/wrappers.md
   Making Your Own <environments/making_new_environments.md>
   
   
.. toctree::
   :maxdepth: 3
   :caption: Learning Setup
   :hidden:
   
   learning/overview.md
   learning/system.md
   learning/on_policy_supervision.md

.. toctree::
   :maxdepth: 3
   :caption: Python API
   :hidden:
   
   neverwhere <api/neverwhere.md>
   neverwhere.render_nodes <api/render_nodes.md>
   neverwhere.trajectory_sampler <api/trajectory_sampler.md>
   neverwhere.scripts <api/scripts.md>
   neverwhere.utils <api/utils.md>
    
```
