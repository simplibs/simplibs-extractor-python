from typing import Final
from simplibs.text.presets import COMPACT
# Outers
from ..actions import (
    RemovePythonComments,
    RemovePythonDecorators,
    RemovePythonDocstrings,
    RemovePythonImports,
)


PYTHON_NO_IMPORTS: Final = (
    RemovePythonComments()
    >> RemovePythonDocstrings()
    >> RemovePythonImports()
    >> RemovePythonDecorators()
    >> COMPACT
)
"""Python reduced to its logic: no comments, docstrings, imports or decorators, and no blank lines."""


_DESIGN_NOTES = """
# PYTHON_NO_IMPORTS — The Logic and Nothing Else

## Purpose
The steps of `python/code-no-imports`.

## Compact, Not Tidy
`COMPACT` removes every blank line, also those inside multi-line strings. This is
the shortest form, meant for a reader (or a model) that needs the code and
not its layout.
"""
