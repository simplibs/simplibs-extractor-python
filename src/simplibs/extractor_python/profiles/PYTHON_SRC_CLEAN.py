from typing import Final
from simplibs.extractor import Profile, by_suffix
# Outers
from ..constants import PYTHON_SUFFIXES
from ..file_rules import PYTHON_BASE, PYTHON_STRICT_EXCLUDE
from ..presets import PYTHON_CLEAN


PYTHON_SRC_CLEAN: Final[Profile] = Profile(
    system="python",
    name="src-clean",
    description="Like code-clean, without tests, configuration, environments and build folders",
    include=PYTHON_BASE,
    exclude=PYTHON_STRICT_EXCLUDE,
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_src_clean.md",
)
"""The profile `python/src-clean`."""


_DESIGN_NOTES = """
# PYTHON_SRC_CLEAN — `python/src-clean`

## Purpose
The old strict file filter made visible: the old code defined it and no profile
ever used it. Only what the project does.

## Output
`python_src_clean.md`.
"""
