from simplibs.text import remove_spans
from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from .python_comment_spans import python_comment_spans


@validate_call
def remove_python_comments(text: str, *, on_error: OnError = "raise") -> str:
    """Remove all comments from a Python source.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card when the text cannot be tokenized, `"keep"` to return it unchanged.

    Returns:
        The text without comments. A line that held only a comment disappears.

    Raises:
        ParamError: The text cannot be tokenized and `on_error` is `"raise"`.
    """

    # 1. Find the comments
    spans = python_comment_spans(text, on_error=on_error)

    # 2. Cut them; strings that merely contain a `#` were never found
    return remove_spans(text, spans)


_DESIGN_NOTES = """
# remove_python_comments — The Comments Out, The Code Untouched

## Purpose
A step of the profiles `python/code-clean` and `python/code-no-imports`.

## Guarantee
For a text that parses, the syntax tree of the result is the same as the tree
of the original: nothing but comments (and the blanks and empty lines they
left) is removed.

## Idempotent
A second run finds nothing and returns the very same text.
"""
