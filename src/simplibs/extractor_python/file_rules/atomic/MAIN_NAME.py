from typing import Final
from simplibs.path.rules import NameIs
from simplibs.rules import Equals, Rule


MAIN_NAME: Final[Rule] = NameIs(Equals("__main__.py"))
"""The file is called `__main__.py`."""


_DESIGN_NOTES = """
# MAIN_NAME — What Runs With `python -m`

## Purpose
The entry point of a package. `build_python_base()` takes it unless
`include_main=False`.
"""
