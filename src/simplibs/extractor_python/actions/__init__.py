from .PythonOutline import PythonOutline
from .RemovePythonComments import RemovePythonComments
from .RemovePythonDecorators import RemovePythonDecorators
from .RemovePythonDocstrings import RemovePythonDocstrings
from .RemovePythonImports import RemovePythonImports


__all__ = [
    "PythonOutline",
    "RemovePythonComments",
    "RemovePythonDecorators",
    "RemovePythonDocstrings",
    "RemovePythonImports",
]


_DESIGN_NOTES = """
# simplibs.extractor_python.actions — The Steps as Pipeline Actions

## Purpose
Every step of `logic/` as an `Action` of `simplibs-actions`, so it can be
chained with `>>` and used as the `steps` of an extractor profile.

    from simplibs.extractor_python.actions import RemovePythonComments, RemovePythonImports
    steps = RemovePythonComments() >> RemovePythonImports()

## Domain Folder
`actions/` has its own `__all__` and is not re-exported from the package root:
a function and an action are different kinds of thing and stay visibly
different at the import line.

## Thin Wrappers
Each action is `create_action(function, main_param="text", ...)`. The options
of the function (`on_error`, `docstrings`) are the options of the action.

## Internal Components Registry

| Component                | Type   | Description                                         |
| :----------------------- | :----- | :-------------------------------------------------- |
| `PythonOutline`          | Action | Over `python_outline`.                              |
| `RemovePythonComments`   | Action | Over `remove_python_comments`.                      |
| `RemovePythonDecorators` | Action | Over `remove_python_decorators`.                    |
| `RemovePythonDocstrings` | Action | Over `remove_python_docstrings`.                    |
| `RemovePythonImports`    | Action | Over `remove_python_imports`.                       |
"""
