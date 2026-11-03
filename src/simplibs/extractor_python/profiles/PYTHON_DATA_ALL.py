from typing import Final
from simplibs.extractor import Profile
# Outers
from ..file_rules import PYTHON_BASE


PYTHON_DATA_ALL: Final[Profile] = Profile(
    system="python",
    name="data-all",
    description="Every relevant .py file, as it is",
    include=PYTHON_BASE,
    output_name="python_data_all.md",
)
"""The profile `python/data-all`."""


_DESIGN_NOTES = """
# PYTHON_DATA_ALL — `python/data-all`

## Purpose
The old `PYTHON_DATA_ALL`: the files selected by `PYTHON_BASE` and no
transformation. A file that is not valid Python cannot fail here.

## Output
`python_data_all.md`.
"""
