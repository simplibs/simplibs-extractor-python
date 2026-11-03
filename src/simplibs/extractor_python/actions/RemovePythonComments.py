from simplibs.actions import create_action
# Outers
from ..logic import remove_python_comments


RemovePythonComments = create_action(
    remove_python_comments,
    main_param="text",
    class_name="RemovePythonComments",
)
"""Action wrapping `remove_python_comments` — takes the comments out of the Python text flowing in."""


_DESIGN_NOTES = """
# RemovePythonComments — Action Over `remove_python_comments`

## Purpose
`RemovePythonComments() >> RemovePythonDocstrings()`: the comment step as a link of a pipeline, a step of a profile.

## Shape
Main input: `text`. Option: `on_error` (`"raise"` by default, `"keep"`). Text in, text out.
"""
