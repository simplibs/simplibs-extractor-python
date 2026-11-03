from typing import Final
from simplibs.rules import Rule
# Inners
from .build_python_base import build_python_base


PYTHON_BASE: Final[Rule] = build_python_base()
"""The default rule for Python files worth reading: `__init__.py` and `__main__.py` included."""


_DESIGN_NOTES = """
# PYTHON_BASE — The Default Choice of Python Files

## Purpose
`build_python_base()` with its defaults, built once. Every Python profile of
this library uses it as `include`.
"""
