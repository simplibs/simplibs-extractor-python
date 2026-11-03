from .PYTHON_CLEAN import PYTHON_CLEAN
from .PYTHON_NO_IMPORTS import PYTHON_NO_IMPORTS


__all__ = [
    "PYTHON_CLEAN",
    "PYTHON_NO_IMPORTS",
]


_DESIGN_NOTES = """
# simplibs.extractor_python.presets — Ready-Made Pipeline Steps

## Purpose
Chains of actions that the profiles use, built once.

    from simplibs.extractor_python.presets import PYTHON_CLEAN
    steps = PYTHON_CLEAN

## Domain Folder
`presets/` has its own `__all__` and is not re-exported from the package root.
It stands to the right of `actions` (it uses them) and to the left of `profiles`.

## Internal Components Registry

| Component           | Type   | Description                                                |
| :------------------ | :----- | :--------------------------------------------------------- |
| `PYTHON_CLEAN`      | Preset | Python without comments and docstrings, whitespace tidied. |
| `PYTHON_NO_IMPORTS` | Preset | Python logic only, compact.                                |
"""
