from typing import Final
from simplibs.extractor import Profile
# Inners
from .PYTHON_CODE_CLEAN import PYTHON_CODE_CLEAN
from .PYTHON_CODE_NO_IMPORTS import PYTHON_CODE_NO_IMPORTS
from .PYTHON_DATA_ALL import PYTHON_DATA_ALL
from .PYTHON_OUTLINE import PYTHON_OUTLINE
from .PYTHON_SRC_CLEAN import PYTHON_SRC_CLEAN


PYTHON_PROFILES: Final[tuple[Profile, ...]] = (
    PYTHON_CODE_CLEAN,
    PYTHON_CODE_NO_IMPORTS,
    PYTHON_DATA_ALL,
    PYTHON_OUTLINE,
    PYTHON_SRC_CLEAN,
)
"""The profiles of the system `python`."""


_DESIGN_NOTES = """
# PYTHON_PROFILES — The `python` System

## Purpose
The profiles of one system in the order the listing commands show them.
"""
