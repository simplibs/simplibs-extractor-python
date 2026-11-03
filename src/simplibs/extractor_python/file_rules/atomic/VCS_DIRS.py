from typing import Final
from simplibs.path import IGNORE_VCS
from simplibs.path.rules import AnyParentNameIs
from simplibs.rules import IsIn, Rule


VCS_DIRS: Final[Rule] = AnyParentNameIs(IsIn(IGNORE_VCS))
"""The file lies inside a version-control folder (`.git`, `.svn`, `.hg`, `.bzr`)."""


_DESIGN_NOTES = """
# VCS_DIRS — Not the Project's Own Files

## Purpose
Part of the strict Python exclusion. The names are `IGNORE_VCS` of
`simplibs-path`: version control is the same for every language, so the
library borrows the list instead of keeping its own.

## What Changed From the Old Code
The old list `VCS_DIR_NAMES` held also `node_modules` and `tmp`. Neither is
version control: `node_modules` belongs to the JavaScript add-on, and `tmp`
is dropped.

## Whole Names Only
`IsIn` compares a folder name as a whole, so `.github` is not `.git`.
"""
