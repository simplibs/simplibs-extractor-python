from typing import Final
from simplibs.path.rules import NameIs
from simplibs.rules import Rule, StartsWith


DOT_NAME: Final[Rule] = NameIs(StartsWith("."))
"""The file name starts with a dot (`.env`, `.hidden.py`)."""


_DESIGN_NOTES = """
# DOT_NAME — Hidden by Convention

## Purpose
Dot files are settings and tool state, not source. Used by both base rules.

## Name Only
Only the name of the file is judged. A visible file inside a `.cache` folder
is not hidden by this rule (the strict exclusions look at folders).
"""
