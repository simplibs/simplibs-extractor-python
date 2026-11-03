from simplibs.actions import create_action
# Outers
from ..logic import remove_python_docstrings


RemovePythonDocstrings = create_action(
    remove_python_docstrings,
    main_param="text",
    class_name="RemovePythonDocstrings",
)
"""Action wrapping `remove_python_docstrings` — takes the docstrings out of the Python text flowing in."""


_DESIGN_NOTES = """
# RemovePythonDocstrings — Action Over `remove_python_docstrings`

## Purpose
The docstring step as a link of a pipeline.

## Shape
Main input: `text`. Option: `on_error`. Text in, text out; a body left empty gets `pass`.
"""
