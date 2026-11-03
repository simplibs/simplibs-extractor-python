from typing import Final
from simplibs.path.rules import AnyParentNameIs
from simplibs.rules import Rule, StartsWith


IN_DUNDER_DIR: Final[Rule] = AnyParentNameIs(StartsWith("__"))
"""Some folder above the file has a name that starts with two underscores (`__pycache__`)."""


_DESIGN_NOTES = """
# IN_DUNDER_DIR — Folders Python Makes by Itself

## Purpose
`__pycache__` and `__pypackages__` hold what the interpreter produced, never
source. Used by `build_python_base()`.
"""
