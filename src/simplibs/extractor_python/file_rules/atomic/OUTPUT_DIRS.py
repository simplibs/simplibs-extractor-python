from typing import Final
from simplibs.path.rules import AnyParentNameIs
from simplibs.rules import IsIn, Rule
# Outers
from ...constants import PYTHON_OUTPUT_DIR_NAMES


OUTPUT_DIRS: Final[Rule] = AnyParentNameIs(IsIn(PYTHON_OUTPUT_DIR_NAMES))
"""The file lies inside a build-output folder."""


_DESIGN_NOTES = """
# OUTPUT_DIRS — Generated Files

## Purpose
Part of the strict Python exclusion. See `PYTHON_OUTPUT_DIR_NAMES`.
"""
