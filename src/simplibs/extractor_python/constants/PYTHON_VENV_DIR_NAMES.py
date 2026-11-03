from typing import Final


PYTHON_VENV_DIR_NAMES: Final[tuple[str, ...]] = ("venv", ".venv", "env", "virtualenv")
"""Names under which a Python virtual environment usually lives."""


_DESIGN_NOTES = """
# PYTHON_VENV_DIR_NAMES — Where Installed Packages Hide

## Purpose
The names behind `VENV_DIRS`. A virtual environment holds thousands of files
that are not the project.

## Known Limit
A folder called `env` that is something else (a settings package, say) is
excluded by the strict rules. The base rules do not look at these names.
"""
