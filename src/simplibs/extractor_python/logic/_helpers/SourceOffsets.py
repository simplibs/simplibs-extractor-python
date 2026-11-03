import ast


class SourceOffsets:
    """Turns the positions `ast` and `tokenize` report into offsets in the text.

    `ast` counts a column in UTF-8 BYTES, `tokenize` in characters; a span has to be in
    characters, because that is what a string is cut by.

    Example:
        offsets = SourceOffsets(text)
        start, end = offsets.span_of(node)
    """

    __slots__ = ("_text", "_starts", "_is_ascii")

    def __init__(self, text: str) -> None:

        # 1. The offset where each line begins
        starts = [0]
        position = 0
        for line in text.split("\n")[:-1]:
            position += len(line) + 1
            starts.append(position)

        # 2. Keep what the conversions need
        self._text = text
        self._starts = starts
        self._is_ascii = text.isascii()

    def token_offset(self, row: int, column: int) -> int:
        """The offset of a `tokenize` position (1-based row, column in characters)."""

        # 1. Characters already: only the start of the line is added
        return self._starts[row - 1] + column

    def ast_offset(self, lineno: int, column: int) -> int:
        """The offset of an `ast` position (1-based line, column in UTF-8 bytes)."""

        # 1. Where the line begins
        start = self._starts[lineno - 1]

        # 2. Only ASCII text has one byte per character
        if self._is_ascii or column == 0:
            return start + column

        # 3. Count the characters that fit into that many bytes
        end = self._text.find("\n", start)
        line = self._text[start:] if end == -1 else self._text[start:end]
        return start + len(line.encode("utf-8")[:column].decode("utf-8"))

    def span_of(self, node: ast.AST) -> tuple[int, int]:
        """The `(start, end)` of a node, in characters."""

        # 1. Both ends of the node
        return (
            self.ast_offset(node.lineno, node.col_offset),
            self.ast_offset(node.end_lineno, node.end_col_offset),
        )


_DESIGN_NOTES = """
# SourceOffsets — Bytes Become Characters

## Purpose
`ast` reports `col_offset` in UTF-8 bytes. In a line with `é` or `€` before
the node, a byte column is NOT a character column, and a cut by it lands in
the wrong place. Every step that cuts by `ast` positions goes through this
class.

## Why a Class
The line table is built once per text and used for every node.

## ASCII Is the Common Case
For a text of ASCII only, a byte and a character are the same thing and the
conversion is an addition.

## Line Endings
Lines are split by `\\n` only, which is what `ast` and `tokenize` count for a
text that has only `\\n`; the steps refuse a text with `\\r` before they get
here.
"""
