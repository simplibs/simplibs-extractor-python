from simplibs.actions import create_action
# Outers
from ..logic import remove_python_imports


RemovePythonImports = create_action(
    remove_python_imports,
    main_param="text",
    class_name="RemovePythonImports",
)
"""Action wrapping `remove_python_imports` — takes the import statements out of the Python text flowing in."""


_DESIGN_NOTES = """
# RemovePythonImports — Action Over `remove_python_imports`

## Purpose
The import step as a link of a pipeline.

## Shape
Main input: `text`. Option: `on_error`. Text in, text out.
"""
