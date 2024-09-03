# Getting Started

Setting up the conda environment:

```python
conda create -n neverwhere python=3.8
conda activate neverwhere
```

Now install the latest version (`{VERSION}`) on [pypi](https://pypi.org/project/neverwhere/{VERSION}/).

```python
pip install -U 'neverwhere[all]=={VERSION}'
```

```{admonition}
:class: tip
    the "`" around the [all] is needed in `zsh`, to prevent shell expansion.
```

You can test the environment by running the following example:

```python
from neverwhere import neverwhere

env = neverwhere.make("Env-name-v1")
obs = env.reset()
done = False

while not done:
    # randomly sample an action
    act = env.action_space.sample()
  
    obs, reward, done, info = env.step()
```

For list of environments, refer to [./environments](environments)

## Developing (Optional)

If you want to develop neverwhere, you can install it in editable mode plus dependencies
relevant for building the documentations:

```shell
cd neverwhere
pip install -e '.[all]'
```

To view the documentations, you can run the `sphinx-autobuild` tool which watches
the current docs directory for changes and refreshes the webpage upon source change.

```shell
make preview
```

To view a static build,

```shell
make docs
```
