from typing import Final
from simplibs.text.presets import CLEANUP_WHITESPACE
# Outers
from ..actions import RemovePythonComments, RemovePythonDocstrings


PYTHON_CLEAN: Final = (
    RemovePythonComments()
    >> RemovePythonDocstrings()
    >> CLEANUP_WHITESPACE
)
"""Python without comments and docstrings, whitespace tidied: the imports stay."""


_DESIGN_NOTES = """
# PYTHON_CLEAN — The Everyday Clean Read

## Purpose
The steps of `python/code-clean` and `python/src-clean` as one object, built once.

## Order
Comments first, then docstrings (both find their targets in the original
structure), whitespace last, to tidy the holes the first two left.

## The Whitespace Step
`CLEANUP_WHITESPACE` squeezes blank runs to one line; it does not remove them.
Code stays in paragraphs a person can read. See `PYTHON_NO_IMPORTS` for the
compact form.
"""
