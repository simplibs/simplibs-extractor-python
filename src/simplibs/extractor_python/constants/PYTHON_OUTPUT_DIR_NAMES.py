from typing import Final


PYTHON_OUTPUT_DIR_NAMES: Final[tuple[str, ...]] = ("build", "dist", "out")
"""Names of folders that hold generated build output of a Python project."""


_DESIGN_NOTES = """
# PYTHON_OUTPUT_DIR_NAMES — Generated, Not Written

## Purpose
The names behind `OUTPUT_DIRS`. Build output repeats the source in another
shape; reading it twice only costs tokens.

## Own List
The library keeps its own list instead of borrowing one: what counts as
build output differs from language to language, and each add-on decides it
for its own language.
"""
