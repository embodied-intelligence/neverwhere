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
    - [neverwhere Basics](tutorials/basics)
    - [Tutorial for Roboticists](tutorials/robotics)
- or try to take a look at the example gallery [here](examples/01_trimesh)

For comprehensive documentation on the python API, please refer to
the [API documentation on Components | neverwhere](https://neverwhere.readthedocs.com/en/latest/api/neverwhere.html).

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
   :caption: NEW FEATURES 🔥
   :hidden:
   
   Scene Generation (OpenAI Sora) <gaussian_splatting/openai_sora.md>
   Gaussian Splatting <gaussian_splatting/09_gaussian_splats.md>
   Gaussian Splatting (VR) <gaussian_splatting/10_gaussian_splats_vr.md>
   
.. toctree::
   :maxdepth: 3
   :caption: Tutorials
   :hidden:
   
   tutorials/basics.md
   tutorials/robotics.md
   tutorials/camera/README.md
   
.. toctree::
   :maxdepth: 3
   :caption: Examples
   :hidden:
   
   Mesh <examples/01_trimesh.md>
   
.. toctree::
   :maxdepth: 3
   :caption: LucidSim
   :hidden:
   
   Sphere Scene <examples/lucidsim/ball_scene.md>
   Stairs Scene <examples/lucidsim/stairs_scene.md>
   Adding UV and Texture Map to Trimesh <examples/lucidsim/textured_trimesh.md>

.. toctree::
   :maxdepth: 3
   :caption: Python API
   :hidden:
   
   neverwhere <api/neverwhere.md>
   neverwhere.base <api/base.md>
   neverwhere.types — Type Interafce <api/types.md>
   neverwhere.events — Event Types <api/events.md>
   neverwhere.schemas — Components <api/schemas.md>
   neverwhere.serdes — Serialization <api/serdes.md>
    
```
