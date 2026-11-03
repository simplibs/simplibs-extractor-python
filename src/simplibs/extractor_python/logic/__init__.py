from .python_comment_spans import python_comment_spans
from .python_outline import python_outline
from .remove_python_comments import remove_python_comments
from .remove_python_decorators import remove_python_decorators
from .remove_python_docstrings import remove_python_docstrings
from .remove_python_imports import remove_python_imports


_DESIGN_NOTES = """
# logic — The Steps That Read Python

Plain imports, no `__all__` (the package root decides what is public).

## Internal Components Registry

| Component                  | Type     | Description                                                      |
| :------------------------- | :------- | :--------------------------------------------------------------- |
| `python_comment_spans`     | Function | The spans of the comments (by `tokenize`).                       |
| `python_outline`           | Function | Classes and functions as signatures without bodies.              |
| `remove_python_comments`   | Function | Removes the comments.                                            |
| `remove_python_decorators` | Function | Removes the decorators of classes and functions.                 |
| `remove_python_docstrings` | Function | Removes the docstrings; an emptied body gets `pass`.             |
| `remove_python_imports`    | Function | Removes the imports at any depth; an emptied body gets `pass`.   |
| `_helpers`                 | Private  | Offsets, the parser guard, statement cutting, finders, outline.  |
| `_validations`             | Private  | The card of an unreadable source.                                |

## Layering & Design
- Python is read with `ast` and `tokenize`, never with a regex.
- Each step is a function of a text and returns a text; the `Action` wrappers come in `actions`.
- `on_error` is `"raise"` by default: a file that cannot be read is reported, not silently left unclean.
- The steps import only `annotations`; the ranges they find are `simplibs.text.Span`.
"""
