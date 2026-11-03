from typing import Final


PYTHON_SUFFIXES: Final[tuple[str, ...]] = (".py",)
"""The suffixes of Python source files."""


_DESIGN_NOTES = """
# PYTHON_SUFFIXES — What Counts as Python Source

## Purpose
One place for the suffixes the Python rules and profiles look for.

## Only `.py`
Stub files (`.pyi`) and Windows scripts (`.pyw`) are not source to read: a
stub only repeats the signatures of a module that is in the output anyway.
"""
