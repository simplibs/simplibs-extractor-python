from .SourceOffsets import SourceOffsets
from .collect_definitions import collect_definitions
from .cut_statements import cut_statements
from .describe_source_failure import describe_source_failure
from .find_decorator_spans import find_decorator_spans
from .find_docstrings import find_docstrings
from .find_imports import find_imports
from .first_doc_line import first_doc_line
from .format_type_params import format_type_params
from .guarded_parse import guarded_parse
from .outline_node import outline_node
from .parse_python import parse_python


_DESIGN_NOTES = """
# _helpers — Shared Tools of the Python Steps

Private. Plain imports, no `__all__`.

## Internal Components Registry

| Component                 | Type     | Description                                                          |
| :------------------------ | :------- | :------------------------------------------------------------------- |
| `SourceOffsets`           | Class    | Turns `ast` byte columns and `tokenize` positions into offsets.      |
| `collect_definitions`     | Function | The classes and functions a body defines, looking through blocks.    |
| `cut_statements`          | Function | Removes simple statements; empty blocks get `pass`.                  |
| `describe_source_failure` | Function | An exception of a parser as a reason and a line.                     |
| `find_decorator_spans`    | Function | The span of every decorator, from its `@`.                           |
| `find_docstrings`         | Function | The docstring statements of a module.                                |
| `find_imports`            | Function | Every import statement, at any depth.                                |
| `first_doc_line`          | Function | The first line of a docstring as a trailing comment.                 |
| `format_type_params`      | Function | `[T, U: int]` of a class or function (Python 3.12+).                 |
| `guarded_parse`           | Function | Runs a parser; decides by `on_error` what a failure means.          |
| `outline_node`            | Function | The signature lines of one class or function.                        |
| `parse_python`            | Function | `ast.parse` under the guard.                                         |
"""
