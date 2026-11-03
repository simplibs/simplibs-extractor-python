import ast
from simplibs.text import Span
# Inners
from .SourceOffsets import SourceOffsets


def _line_start(text: str, position: int) -> int:
    """The offset where the line holding `position` begins."""
    return max(text.rfind("\n", 0, position), text.rfind("\r", 0, position)) + 1


def _end_of_line(text: str, position: int) -> int:
    """The offset of the line break that ends the line holding `position` (or the end of the text)."""
    while position < len(text) and text[position] not in "\r\n":
        position += 1
    return position


def _count_opening_brackets(text: str, begin: int, stop: int) -> int:
    """Count the `(` in `text[begin:stop]`, leaving out comments."""
    count = 0
    position = begin
    while position < stop:
        if text[position] == "#":
            position = _end_of_line(text, position)
            continue
        if text[position] == "(":
            count += 1
        position += 1
    return count


def _skip_filler(text: str, position: int) -> int:
    """The offset of the first character from `position` on that is no blank, line break or comment."""
    while position < len(text) and (text[position] in " \t\f\r\n" or text[position] == "#"):
        position = _end_of_line(text, position) if text[position] == "#" else position + 1
    return position


def find_decorator_spans(text: str, tree: ast.Module, offsets: SourceOffsets) -> list[Span]:
    """Find the decorators of every class and function, each from its `@` to its end.

    Args:
        text: The source the tree was parsed from.
        tree: The parsed module.
        offsets: The offsets of `text`.

    Returns:
        One span per decorator.
    """

    # 1. Every decorator of every class and function
    spans: list[Span] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for decorator in node.decorator_list:
            start, end = offsets.span_of(decorator)

            # 2. The `@` stands in front of the expression; an `@` with a `#` before it on its line is in a comment
            at = text.rfind("@", 0, start)
            while "#" in text[_line_start(text, at):at]:
                at = text.rfind("@", 0, at)

            # 3. `@(factory)`: the node does not include its own brackets, so the closing ones are taken too
            #    (the text parsed, so every opening bracket has its closing one behind the expression)
            for _ in range(_count_opening_brackets(text, at + 1, start)):
                end = _skip_filler(text, end) + 1

            spans.append((at, end))

    return spans


_DESIGN_NOTES = """
# find_decorator_spans — From the `@` to the End of the Expression

## Purpose
`ast` gives the position of the decorator's EXPRESSION, not of the `@`. The
span has to start at the `@`, or what is left is a line holding a lone `@`.

## Why `rfind`, and Why a Check After It
The nearest `@` in front of the expression is the decorator's own: between
them stand only blanks, opening brackets and, inside brackets, comments. A
comment may hold an `@` of its own (`# mail me@home`), so one more rule is
needed: the real `@` is the first thing on its line, hence an `@` with a `#`
in front of it on its line belongs to a comment and is skipped.

## Bracketed Decorators
`@(lambda f: f)` is valid since Python 3.9. The expression node starts after
the `(` and ends before the `)`, so a cut by the node alone would leave a
stray bracket. The brackets in front of the expression are counted and the
same number of closing ones is taken after it. The text parsed, so every
opening bracket has its closing one behind the expression; there is nothing
to check, only to find.

## Comments Inside the Brackets
Between the `@` and the expression, and between the expression and its `)`,
no string can stand, so a `#` there always starts a comment. Such a comment
is skipped when counting the brackets and when looking for the closing one
(`@(dec  # note)` + line break + `)` has its real `)` on the next line), and
it stays inside the span.

## What Stays
A comment AFTER the decorator (`@dec  # note`) is not part of it. Comments are
a step of their own, normally run first.
"""
