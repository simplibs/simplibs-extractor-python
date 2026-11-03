import ast
# Outers
from ...annotations import OnError
# Inners
from .guarded_parse import guarded_parse


def parse_python(text: str, on_error: OnError) -> ast.Module | None:
    """Parse a text as Python source.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card, `"keep"` for `None`.

    Returns:
        The syntax tree; `None` if the text cannot be parsed and `on_error` is `"keep"`.

    Raises:
        ParamError: The text cannot be parsed and `on_error` is `"raise"`.
    """

    # 1. `ast.parse` under the guard
    return guarded_parse(text, on_error, ast.parse)


_DESIGN_NOTES = """
# parse_python — The Tree or Nothing

## Purpose
The first line of every step that works on the structure of a module.
`None` means "leave the text alone" and the caller returns it as it was.
"""
