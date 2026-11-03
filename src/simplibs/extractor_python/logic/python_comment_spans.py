import io
import tokenize
from simplibs.text import Span
from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from ._helpers import SourceOffsets, guarded_parse


def _collect_comment_spans(text: str) -> list[Span]:
    """Run the tokenizer and turn every comment token into a span."""

    # 1. Every COMMENT token, with the blanks in front of it
    offsets = SourceOffsets(text)
    spans: list[Span] = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        start = offsets.token_offset(*token.start)
        end = offsets.token_offset(*token.end)
        while start > 0 and text[start - 1] in " \t":
            start -= 1
        spans.append((start, end))

    return spans


@validate_call
def python_comment_spans(text: str, *, on_error: OnError = "raise") -> list[Span]:
    """Find the comments of a Python source.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card when the text cannot be tokenized, `"keep"` for no spans.

    Returns:
        A span for each comment, from the blanks in front of it to the end of the comment.

    Raises:
        ParamError: The text cannot be tokenized and `on_error` is `"raise"`.
    """

    # 1. Tokenize under the guard
    spans = guarded_parse(text, on_error, _collect_comment_spans)

    # 2. A text that could not be read has no spans
    return spans or []


_DESIGN_NOTES = """
# python_comment_spans — Comments Found by the Tokenizer

## Purpose
Where the comments are, as spans that `remove_spans` can cut.

## Why `tokenize` and Not a Regex
A `#` inside a string (`"a # b"`, `'''# not a comment'''`) is not a comment, and
telling the two apart is the tokenizer's job. A regex gets it wrong exactly in
the files where it matters.

## The Blanks in Front
`x = 1  # note` is cut to `x = 1`, not to `x = 1  `. A comment on a line of its
own is taken with its indentation, and the cut removes the empty line.

## Shebang and Coding Line
`#!/usr/bin/env python` and `# -*- coding: utf-8 -*-` are comments to the
tokenizer and go with the rest: the output is for reading, not for running.

## What It Needs
Only that the text can be TOKENIZED, not that it is valid Python 3: a file that
`ast` refuses may still have its comments found.
"""
