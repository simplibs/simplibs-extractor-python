from typing import Final
from simplibs.rules import Rule
# Outers
from ..atomic import OUTPUT_DIRS, VCS_DIRS, VENV_DIRS
# Inners
from .PYTHON_CONFIG import PYTHON_CONFIG
from .PYTHON_TESTS import PYTHON_TESTS


PYTHON_STRICT_EXCLUDE: Final[Rule] = PYTHON_TESTS | PYTHON_CONFIG | VENV_DIRS | OUTPUT_DIRS | VCS_DIRS
"""Everything that is Python-looking but not the project's own logic: tests, configuration, environments, build output."""


_DESIGN_NOTES = """
# PYTHON_STRICT_EXCLUDE — Only What the Project Does

## Purpose
The `exclude` of the profile `python/src-clean`. The old code had a strict
filter like this, but no profile ever used it.

## How It Combines
Used together with `PYTHON_BASE` as `include`: a file must be Python source
and must not be any of these.
"""
