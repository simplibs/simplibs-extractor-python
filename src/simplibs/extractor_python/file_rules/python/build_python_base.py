from simplibs.path.rules import HasSuffix
from simplibs.rules import Rule
from simplibs.validate import validate_call
# Outers
from ...constants import PYTHON_SUFFIXES
from ..atomic import DOT_NAME, IN_DUNDER_DIR, INIT_NAME, MAIN_NAME


@validate_call
def build_python_base(*, include_init: bool = True, include_main: bool = True) -> Rule:
    """Build the rule that picks the Python files worth reading.

    Python files, without dot files and without anything inside a folder such
    as `__pycache__`.

    Args:
        include_init: Take `__init__.py`. Switch off to read only the modules.
        include_main: Take `__main__.py`. Switch off to leave the entry point out.

    Returns:
        A rule on the path relative to the source folder.
    """

    # 1. The core: Python files that are not hidden and not interpreter products
    rule = HasSuffix(*PYTHON_SUFFIXES) & ~DOT_NAME & ~IN_DUNDER_DIR

    # 2. The two package files, unless asked to leave them out
    if not include_init:
        rule = rule & ~INIT_NAME
    if not include_main:
        rule = rule & ~MAIN_NAME

    return rule


_DESIGN_NOTES = """
# build_python_base — Which Python Files Are Source

## Purpose
The `include` of every Python profile, with two switches for the files the old
code always dropped.

## What Changed From the Old `PythonBase`
The old rule excluded every file whose name starts with two underscores.
That took away `__init__.py`, which holds the public names of a package, and
`__main__.py`, the entry point. Now both are taken by default; the switches
bring back the old behaviour. Other names of that kind (`__version__.py`,
`__about__.py`) are ordinary modules and are taken as well.

## Folders
A folder whose name starts with two underscores is still left out
(`__pycache__`, `__pypackages__`): it holds what the interpreter made.

## Why the Name Starts With `build_`
The constant `PYTHON_BASE` has its own file. On Windows and macOS two files
whose names differ only by case (`python_base.py`, `PYTHON_BASE.py`) are the
same file, so the function got a name that differs by more than the case.
"""
