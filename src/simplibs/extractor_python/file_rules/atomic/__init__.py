from .DOT_NAME import DOT_NAME
from .INIT_NAME import INIT_NAME
from .IN_DUNDER_DIR import IN_DUNDER_DIR
from .MAIN_NAME import MAIN_NAME
from .OUTPUT_DIRS import OUTPUT_DIRS
from .VCS_DIRS import VCS_DIRS
from .VENV_DIRS import VENV_DIRS


_DESIGN_NOTES = """
# atomic — The Shared Pieces of the File Rules

Plain imports, no `__all__` (the package root decides what is public).

## Internal Components Registry

| Component       | Type | Description                                                  |
| :-------------- | :--- | :----------------------------------------------------------- |
| `DOT_NAME`      | Rule | The name starts with a dot.                                  |
| `INIT_NAME`     | Rule | The name is `__init__.py`.                                   |
| `IN_DUNDER_DIR` | Rule | A folder above the file starts with two underscores.         |
| `MAIN_NAME`     | Rule | The name is `__main__.py`.                                   |
| `OUTPUT_DIRS`   | Rule | A folder above the file is a build-output folder.            |
| `VCS_DIRS`      | Rule | A folder above the file is a version-control folder.         |
| `VENV_DIRS`     | Rule | A folder above the file is a virtual environment.            |

## Layering & Design
- Every piece is one rule of one idea; the `python` folder only combines them.
- The rules about folders use `AnyParentNameIs` of `simplibs-path` and `IsIn` of `simplibs-rules`.
"""
