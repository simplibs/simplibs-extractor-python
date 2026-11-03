from typing import Final
from simplibs.path.rules import AnyParentNameIs, NameIs
from simplibs.rules import IsIn, Regex, Rule
# Outers
from ...constants import PYTHON_TEST_DIR_NAMES


PYTHON_TESTS: Final[Rule] = (
    NameIs(Regex(r"^(test_.*|.*_tests?|tests?|conftest)\.py$"))
    | AnyParentNameIs(IsIn(PYTHON_TEST_DIR_NAMES))
)
"""The file is a Python test: by its name (`test_a.py`, `a_test.py`, `tests.py`, `conftest.py`) or by its folder (`tests/`)."""


_DESIGN_NOTES = """
# PYTHON_TESTS — Recognising a Test by Its Name, Not by a Piece of It

## Purpose
Part of the strict Python exclusion.

## Why a Pattern on the Whole Name
The old rule asked whether the path CONTAINED `test`, and it threw away
`latest_data.py`, `contest.py` and `attest.py`. The pattern is anchored at both
ends: the name starts with `test_`, ends with `_test` or `_tests`, or is
exactly `test`, `tests` or `conftest`, followed by `.py`.

## Or Anywhere Inside a Tests Folder
Every file in a folder called `tests` or `test` is a test helper at least.
"""
