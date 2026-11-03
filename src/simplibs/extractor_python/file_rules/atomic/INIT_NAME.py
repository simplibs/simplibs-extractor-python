from typing import Final
from simplibs.path.rules import NameIs
from simplibs.rules import Equals, Rule


INIT_NAME: Final[Rule] = NameIs(Equals("__init__.py"))
"""The file is called `__init__.py`."""


_DESIGN_NOTES = """
# INIT_NAME — The Face of a Package

## Purpose
`__init__.py` holds the public names and `__all__` of a package, so it is
usually the best single file for understanding one. `build_python_base()`
takes it unless `include_init=False`.
"""
