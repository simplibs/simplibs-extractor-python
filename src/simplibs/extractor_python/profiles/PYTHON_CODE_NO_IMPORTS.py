from typing import Final
from simplibs.extractor import Profile, by_suffix
# Outers
from ..constants import PYTHON_SUFFIXES
from ..file_rules import PYTHON_BASE
from ..presets import PYTHON_NO_IMPORTS


PYTHON_CODE_NO_IMPORTS: Final[Profile] = Profile(
    system="python",
    name="code-no-imports",
    description="Pure logic: no imports, decorators, comments, docstrings or blank lines",
    include=PYTHON_BASE,
    steps=by_suffix(PYTHON_NO_IMPORTS, PYTHON_SUFFIXES),
    output_name="python_code_no_imports.md",
)
"""The profile `python/code-no-imports`."""


_DESIGN_NOTES = """
# PYTHON_CODE_NO_IMPORTS — `python/code-no-imports`

## Purpose
The old `PYTHON_CODE_CLEAN_NO_IMPORTS`: what the code does, not what it is
wired to.

## Output
`python_code_no_imports.md`.
"""
