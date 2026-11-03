import ast
from bisect import bisect_right
from collections.abc import Collection
from simplibs.text import remove_spans
# Inners
from .SourceOffsets import SourceOffsets


_BLOCK_FIELDS = ("body", "orelse", "finalbody")


def _extend_over_semicolon(text: str, start: int, end: int) -> tuple[int, int]:
    """Widen a statement's span over the `;` that joins it to its neighbour on the same line."""

    # 1. A `;` after it: take it and the blanks behind it, so the next statement moves up
    probe = end
    while probe < len(text) and text[probe] in " \t":
        probe += 1
    if probe < len(text) and text[probe] == ";":
        probe += 1
        while probe < len(text) and text[probe] in " \t":
            probe += 1
        return start, probe

    # 2. Otherwise a `;` before it: the statement is the last of its line, take the `;` with it
    probe = start
    while probe > 0 and text[probe - 1] in " \t":
        probe -= 1
    if probe > 0 and text[probe - 1] == ";":
        probe -= 1
        while probe > 0 and text[probe - 1] in " \t":
            probe -= 1
        return probe, end

    # 3. Alone on its line
    return start, end


def cut_statements(
    text: str,
    tree: ast.Module,
    targets: Collection[ast.stmt],
    offsets: SourceOffsets,
) -> str:
    """Remove simple statements from a module and keep the rest valid Python.

    Args:
        text: The source the tree was parsed from.
        tree: The parsed module.
        targets: The statements to remove: simple ones (an import, an expression), never a compound one.
        offsets: The offsets of `text`.

    Returns:
        The text without the statements. A block that would be left empty gets a `pass`.
    """

    # 1. Nothing to cut — the very same text back
    if not targets:
        return text

    # 2. Walk every list of statements, remember what to cut and where a block would be left empty
    spans: list[tuple[int, int]] = []
    pass_positions: list[int] = []
    for node in ast.walk(tree):
        for field in _BLOCK_FIELDS:
            statements = getattr(node, field, None)
            if not isinstance(statements, list) or not statements:
                continue
            hits = [statement for statement in statements if statement in targets]
            if not hits:
                continue
            if len(hits) == len(statements) and not isinstance(node, ast.Module):
                pass_positions.append(offsets.span_of(statements[0])[0])
            for statement in hits:
                start, end = offsets.span_of(statement)
                spans.append(_extend_over_semicolon(text, start, end))

    # 3. Put each `pass` in front of the first statement of its block; the cut then leaves just the `pass`
    pass_positions.sort()
    pieces: list[str] = []
    previous = 0
    for position in pass_positions:
        pieces.append(text[previous:position])
        pieces.append("pass")
        previous = position
    pieces.append(text[previous:])
    padded = "".join(pieces)

    # 4. The spans move with the text: every `pass` inserted at or before an offset pushes it by four
    shifted = [
        (start + 4 * bisect_right(pass_positions, start), end + 4 * bisect_right(pass_positions, end))
        for start, end in spans
    ]

    # 5. Cut; a line that only held a removed statement disappears whole
    return remove_spans(padded, shifted)


_DESIGN_NOTES = """
# cut_statements — Taking Statements Out Without Breaking the Syntax

## Purpose
The one primitive behind `remove_python_docstrings` and
`remove_python_imports`: the caller decides WHICH statements go, this decides
how to remove them so that what is left is still Python.

## The Three Traps
1. **An emptied block.** `try: import x` / `else:` / a class holding only its
   docstring: a block needs a statement. It gets a `pass` — in a module, an
   empty body is fine and gets none.
2. **A statement sharing a line.** `import a; x = 1` and `x = 1; import a`:
   the `;` that joined them goes with the removed statement, the other one
   stays on a line of its own. Without it, `; x = 1` would not parse.
3. **A statement that is not alone on its line.** `import a  # note`: only the
   statement is removed; what remains of the line is what was there besides.

## How the `pass` Gets There
It is inserted in front of the first statement of the block and the whole
block is cut afterwards, so the `pass` takes the place of the removed text,
indentation and all. Offsets are shifted by four for every `pass` in front
of them.

## Why Simple Statements Only
A compound statement (`def`, `if`) contains lists of statements of its own,
and cutting both would count some of them twice. Nothing here needs it.
"""
