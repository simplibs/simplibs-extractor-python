from typing import Final


PYTHON_CONFIG_NAMES: Final[tuple[str, ...]] = (
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "requirements.txt",
    "tox.ini",
    "pytest.ini",
)
"""File names of Python project configuration."""


_DESIGN_NOTES = """
# PYTHON_CONFIG_NAMES — Packaging, Not Logic

## Purpose
Used by `PYTHON_CONFIG`. These files describe how the project is built and
tested; they are not what it does.

## Case
Names are compared exactly. `Pipfile` is written with a capital letter by the
tool that owns it.
"""
