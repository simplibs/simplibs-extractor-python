from .PYTHON_CODE_CLEAN import PYTHON_CODE_CLEAN
from .PYTHON_CODE_NO_IMPORTS import PYTHON_CODE_NO_IMPORTS
from .PYTHON_DATA_ALL import PYTHON_DATA_ALL
from .PYTHON_OUTLINE import PYTHON_OUTLINE
from .PYTHON_PROFILES import PYTHON_PROFILES
from .PYTHON_SRC_CLEAN import PYTHON_SRC_CLEAN


__all__ = [
    "PYTHON_CODE_CLEAN",
    "PYTHON_CODE_NO_IMPORTS",
    "PYTHON_DATA_ALL",
    "PYTHON_OUTLINE",
    "PYTHON_PROFILES",
    "PYTHON_SRC_CLEAN",
]


_DESIGN_NOTES = """
# simplibs.extractor_python.profiles — The Profiles Themselves

## Purpose
The five profiles as `Profile` objects of the extractor. Registering them is
the job of `register_all`; having them as objects lets a program use one
directly or build its own on top of it.

    from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN
    from dataclasses import replace
    mine = replace(PYTHON_SRC_CLEAN, name="mine", output_name="mine.md")

## Domain Folder
`profiles/` has its own `__all__` and is not re-exported from the package root.

## Internal Components Registry

| Component                | Type    | Description                                              |
| :----------------------- | :------ | :------------------------------------------------------- |
| `PYTHON_CODE_CLEAN`      | Profile | `python/code-clean`: comments and docstrings removed.    |
| `PYTHON_CODE_NO_IMPORTS` | Profile | `python/code-no-imports`: the logic only.                |
| `PYTHON_DATA_ALL`        | Profile | `python/data-all`: every Python file as it is.           |
| `PYTHON_OUTLINE`         | Profile | `python/outline`: signatures without bodies.             |
| `PYTHON_PROFILES`        | Tuple   | All five profiles, in the order the listings show them.  |
| `PYTHON_SRC_CLEAN`       | Profile | `python/src-clean`: the project's own logic, cleaned.    |

## Layering & Design
- `by_suffix` (one step for a family of file types) is a tool of `simplibs-extractor`.
"""
