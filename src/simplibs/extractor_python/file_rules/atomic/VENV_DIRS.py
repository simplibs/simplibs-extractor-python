from typing import Final
from simplibs.path.rules import AnyParentNameIs
from simplibs.rules import IsIn, Rule
# Outers
from ...constants import PYTHON_VENV_DIR_NAMES


VENV_DIRS: Final[Rule] = AnyParentNameIs(IsIn(PYTHON_VENV_DIR_NAMES))
"""The file lies inside a Python virtual environment folder."""


_DESIGN_NOTES = """
# VENV_DIRS — The Interpreter's Own Packages

## Purpose
Part of the strict Python exclusion. See `PYTHON_VENV_DIR_NAMES` for the names
and the known limit.
"""
