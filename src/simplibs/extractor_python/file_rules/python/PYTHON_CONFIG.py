from typing import Final
from simplibs.path.rules import NameIs
from simplibs.rules import IsIn, Rule
# Outers
from ...constants import PYTHON_CONFIG_NAMES


PYTHON_CONFIG: Final[Rule] = NameIs(IsIn(PYTHON_CONFIG_NAMES))
"""The file is Python project configuration (`setup.py`, `tox.ini`, `requirements.txt`...)."""


_DESIGN_NOTES = """
# PYTHON_CONFIG — How the Project Is Built

## Purpose
Part of the strict Python exclusion. `setup.py` is Python source, but it
describes packaging; for reading what the project does, it is noise.
"""
