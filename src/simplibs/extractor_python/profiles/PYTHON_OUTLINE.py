from typing import Final
from simplibs.extractor import Profile, by_suffix
# Outers
from ..actions import PythonOutline
from ..constants import PYTHON_SUFFIXES
from ..file_rules import PYTHON_BASE


PYTHON_OUTLINE: Final[Profile] = Profile(
    system="python",
    name="outline",
    description="Overview of classes and functions: signatures without bodies",
    include=PYTHON_BASE,
    steps=by_suffix(PythonOutline(), PYTHON_SUFFIXES),
    output_name="python_outline.md",
)
"""The profile `python/outline`."""


_DESIGN_NOTES = """
# PYTHON_OUTLINE — `python/outline`

## Purpose
New, not in the old code: what a project offers, in a fraction of the size.
For a reader with a limited window the signatures are most of what is needed
to ask the right questions.

## Output
`python_outline.md`; each file is valid Python again.
"""
