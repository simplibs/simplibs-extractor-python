from simplibs.text import remove_spans
from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from ._helpers import SourceOffsets, find_decorator_spans, parse_python


@validate_call
def remove_python_decorators(text: str, *, on_error: OnError = "raise") -> str:
    """Remove the decorators of every class and function of a Python source.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged.

    Returns:
        The text without decorators; the lines they stood on disappear.

    Raises:
        ParamError: The text cannot be parsed and `on_error` is `"raise"`.
    """

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut each decorator from its `@`
    return remove_spans(text, find_decorator_spans(text, tree, SourceOffsets(text)))


_DESIGN_NOTES = """
# remove_python_decorators — The Function, Not How It Is Wrapped

## Purpose
A step of the profile `python/code-no-imports`: `@app.route(...)`,
`@dataclass`, `@property` describe how a function is registered or wrapped,
not what it does.

## Guarantee
For a text that parses, the syntax tree of the result equals the tree of the
original with every `decorator_list` emptied.

## Semantics Change
A decorator can change what a function IS (`@property`, `@staticmethod`,
`@contextmanager`). The output is for reading; it is not meant to be run.
"""
