import tokenize
from collections.abc import Callable
from typing import TypeVar
# Outers
from ...annotations import OnError
from .._validations import raise_python_source_error
# Inners
from .describe_source_failure import describe_source_failure


T = TypeVar("T")


def guarded_parse(text: str, on_error: OnError, parser: Callable[[str], T]) -> T | None:
    """Run a parser over a text and decide what a failure means.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card, `"keep"` for `None`.
        parser: What reads the text (`ast.parse`, a tokenizer loop).

    Returns:
        What the parser returned; `None` if it could not read the text and `on_error` is `"keep"`.

    Raises:
        ParamError: The text cannot be read and `on_error` is `"raise"`.
    """

    # 1. Only `\n` line endings: `ast` and `tokenize` would count lines differently from the offsets
    failure: tuple[str, int | None] | None = None
    if "\r" in text:
        failure = ("it has line endings other than \\n", None)

    # 2. Read it
    else:
        try:
            return parser(text)
        except (SyntaxError, ValueError, RecursionError, tokenize.TokenError) as exc:
            failure = describe_source_failure(exc)

    # 3. What a failure means
    if on_error == "keep":
        return None
    raise_python_source_error(text, *failure)


_DESIGN_NOTES = """
# guarded_parse — One Place Where Reading Fails

## Purpose
The steps of this domain all need a reader (`ast.parse`, `tokenize`) and all
have the same question when it fails. This is where it is answered, once.

## The Exceptions
`SyntaxError` (and its `IndentationError`), `ValueError` (a null byte, before
Python 3.12), `RecursionError` (a source nested deeper than the parser
goes) and `tokenize.TokenError` (an unterminated string or bracket).
Anything else is a bug and is not hidden.

## Why `\\r` Is a Failure
`ast` counts a lone `\\r` as a line end, the offset table does not. A cut by
such a position would land on a wrong line, so the text is refused. The
extractor never gives it one: the reader hands over `\\n` only.
"""
