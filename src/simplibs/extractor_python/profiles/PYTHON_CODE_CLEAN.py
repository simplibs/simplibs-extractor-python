from typing import Final
from simplibs.extractor import Profile, by_suffix
# Outers
from ..constants import PYTHON_SUFFIXES
from ..file_rules import PYTHON_BASE
from ..presets import PYTHON_CLEAN


PYTHON_CODE_CLEAN: Final[Profile] = Profile(
    system="python",
    name="code-clean",
    description="Python without comments, docstrings and extra blank lines (imports stay)",
    include=PYTHON_BASE,
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_code_clean.md",
)
"""The profile `python/code-clean`."""


_DESIGN_NOTES = """
# PYTHON_CODE_CLEAN — `python/code-clean`

## Purpose
The old `PYTHON_CODE_CLEAN`: the code with its prose taken away.

## Output
`python_code_clean.md`. A file that is not valid Python makes THAT file an
`error` in the report; the others are not affected.
"""
