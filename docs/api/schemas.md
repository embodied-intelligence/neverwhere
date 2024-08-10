# Component Library<br/>`neverwhere.schemas`

`neverwhere.schema` contains the schemas for the various components of the neverwhere system. These schemas are used to validate the data that is passed
to the various components of the system.

For detailed view of how these components are implemented, please refer to the typescript source code
at [https://github.com/neverwhere-ai/neverwhere-ts/tree/master/src/schemas](https://github.com/neverwhere-ai/neverwhere-ts/tree/master/src/schemas).

**Example Usage:**

```python
from neverwhere import neverwhere
from neverwhere.schemas import DefaultScene, Sphere

neverwhere = neverwhere()
neverwhere.set @ DefaultScene(up=[0, 1, 0])
neverwhere.upsert @ Sphere(args=[0.1, 20, 20], position=[0, 0.1, 0], key="sphere")
```

## HTML Components

```{eval-rst}
.. automodule:: neverwhere.schemas.html_components
   :members:
   :undoc-members:
   :exclude-members: __init__, Coroutine, CancelledError, partial, Path
   :show-inheritance:
```

## 3D Scene Components

```{eval-rst}
.. automodule:: neverwhere.schemas.scene_components
   :members:
   :undoc-members:
   :exclude-members: __init__, Coroutine, CancelledError, partial, Path
   :show-inheritance:
```

## Drei Components

```{eval-rst}
.. automodule:: neverwhere.schemas.drei_components
   :members:
   :undoc-members:
   :exclude-members: __init__, Coroutine, CancelledError, partial, Path
   :show-inheritance:
```
