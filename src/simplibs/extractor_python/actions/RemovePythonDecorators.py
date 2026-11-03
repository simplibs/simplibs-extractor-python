from simplibs.actions import create_action
# Outers
from ..logic import remove_python_decorators


RemovePythonDecorators = create_action(
    remove_python_decorators,
    main_param="text",
    class_name="RemovePythonDecorators",
)
"""Action wrapping `remove_python_decorators` — takes the decorators off the classes and functions of the Python text flowing in."""


_DESIGN_NOTES = """
# RemovePythonDecorators — Action Over `remove_python_decorators`

## Purpose
The decorator step as a link of a pipeline.

## Shape
Main input: `text`. Option: `on_error`. Text in, text out.
"""
