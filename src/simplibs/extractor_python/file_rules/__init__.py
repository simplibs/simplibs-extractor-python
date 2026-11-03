from .atomic import (
    DOT_NAME,
    INIT_NAME,
    IN_DUNDER_DIR,
    MAIN_NAME,
    OUTPUT_DIRS,
    VCS_DIRS,
    VENV_DIRS,
)
from .python import (
    PYTHON_BASE,
    PYTHON_CONFIG,
    PYTHON_STRICT_EXCLUDE,
    PYTHON_TESTS,
    build_python_base,
)


__all__ = [
    # atomic
    "DOT_NAME",
    "INIT_NAME",
    "IN_DUNDER_DIR",
    "MAIN_NAME",
    "OUTPUT_DIRS",
    "VCS_DIRS",
    "VENV_DIRS",
    # python
    "PYTHON_BASE",
    "PYTHON_CONFIG",
    "PYTHON_STRICT_EXCLUDE",
    "PYTHON_TESTS",
    "build_python_base",
]


_DESIGN_NOTES = """
# simplibs.extractor_python.file_rules — Which Files Are Worth Reading

## Purpose
Rules on the path of a file, relative to the source folder. The profiles use
them as `include` and `exclude`; they compose with `&`, `|` and `~`, so a
program can build its own selection from them:

    from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_TESTS
    only_tests = PYTHON_BASE & PYTHON_TESTS

## Domain Folder
`file_rules/` has its own `__all__` and is not re-exported from the package root.

## Internal Components Registry

| Component | Type    | Description                                                   |
| :-------- | :------ | :------------------------------------------------------------ |
| `atomic`  | Package | The shared pieces: dot names, init, main, VCS folders...      |
| `python`  | Package | Rules for Python projects.                                    |

## Layering & Design
- `atomic` ← `python`.
- Every rule is built once, when the package is imported.
- A rule about the folders above a file is `AnyParentNameIs` of `simplibs-path`; a set of names is `IsIn` of `simplibs-rules`.
"""
