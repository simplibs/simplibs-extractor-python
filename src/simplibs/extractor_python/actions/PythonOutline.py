from simplibs.actions import create_action
# Outers
from ..logic import python_outline


PythonOutline = create_action(
    python_outline,
    main_param="text",
    class_name="PythonOutline",
)
"""Action wrapping `python_outline` — turns the Python text flowing in into signatures without bodies."""


_DESIGN_NOTES = """
# PythonOutline — Action Over `python_outline`

## Purpose
The overview step as a link of a pipeline: `PythonOutline(docstrings=False)`.

## Shape
Main input: `text`. Options: `docstrings` (first docstring line as a comment, on by default), `on_error`.
Text in, text out (a valid Python outline).
"""
