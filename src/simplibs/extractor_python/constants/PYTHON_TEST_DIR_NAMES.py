from typing import Final


PYTHON_TEST_DIR_NAMES: Final[tuple[str, ...]] = ("tests", "test")
"""Names of folders that hold Python tests."""


_DESIGN_NOTES = """
# PYTHON_TEST_DIR_NAMES — Where Python Tests Live

## Purpose
Used by `PYTHON_TESTS`: every file in a folder with one of these names is a
test, whatever the file is called.

## Whole Names Only
A folder is compared as a whole (`tests`), never as a part of a name, so
`contest` or `latest` are not tests.
"""
