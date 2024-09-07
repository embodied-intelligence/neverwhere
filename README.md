<h2>neverwhere: Hyper-Realistic Visual Locomotion Benchmark
<br/>
<a href="https://pypi.org/project/neverwhere/">
<img src="https://img.shields.io/pypi/v/neverwhere.svg" alt="pypi">
</a>
<a href="https://docs.neverwhere.ai">
<img src="https://readthedocs.org/projects/neverwhere/badge/?version=latest">
</a>
</h2>
<p>
<strong><code>pip install neverwhere</code></strong>
&nbsp;&nbsp;⬝&nbsp;&nbsp;
visit &ensp;<a href="https://neverwhere.readthedocs.org">https://neverwhere.readthedocs.org</a>&ensp; for documentation
</p>

neverwhere is a hyper realistic visual benchmark for legged locomotion.

## Installation

You can install `neverwhere` with `pip`:

```shell
pip install -U 'neverwhere[all]'
```

- [ ] add setup for the dataset.


```python
from neverwhere import make

env = make("Cones-BCS-v1")

env.reset()
for _ in range(1000):
    random_action = env.action_space.sample()
    env.step(random_action)
    ego_view = env.render("rgb_array")
```

To get a quick overview of what you can do with `neverwhere`, check out the following:

For a comprehensive list of visualization components, please refer to
the [API documentation on Components](https://docs.neverwhere.ai/en/latest/api/neverwhere.html).

For a comprehensive list of data types, please refer to
the [API documentation on Data Types](https://docs.neverwhere.ai/en/latest/api/types.html).

## How to Develop: Contributing to Documentation and Features

Documentation is a crucial part of the `neverwhere` ecosystem.

This repo comes with a autobuild preview of the documentations. You can start it by running the following command and then
open [http://localhost:8000](http://localhost:8000) in your browser.

```shell
pip install -e '.[all]'
make preview
```

To build the documentation, you can run the following that fires up an http server at the port `8888`. You can view the documentation
at [http://localhost:8888](http://localhost:8888).

```shell

```bash
pip install -e '.[all]'
make docs
```

## About Us

neverwhere is built by researchers at MIT, USC and UCSD.
