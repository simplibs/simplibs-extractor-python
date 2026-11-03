from typing import NoReturn
from simplibs.exception import ParamError


def raise_python_source_error(text: str, reason: str, line: int | None = None) -> NoReturn:
    """Raise ParamError when a text cannot be read as Python source.

    Args:
        text: The text that could not be read.
        reason: What is wrong with it, in words.
        line: The line the problem was found on (1-based), if known.
    """

    # 1. The line of the problem is the best value to show; without it, the start of the text
    lines = text.split("\n")
    if line is not None and 1 <= line <= len(lines):
        shown = lines[line - 1].strip()
        where = f" (line {line})"
    else:
        shown = text[:80]
        where = ""

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="CODE_EXTRACTOR_PYTHON_SOURCE_INVALID",
        label="text",
        value=shown,
        problem=f"The text is not Python source I can read: {reason}{where}.",
        expected="Valid Python 3 source with `\\n` line endings.",
        how_to_fix=(
            "Fix the file, or leave it out of the extraction (an `exclude` rule of the profile).",
            "A text with `\\r\\n` or `\\r` endings has to be normalized to `\\n` first.",
            "Pass on_error='keep' to get such a file back unchanged instead of an error.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_python_source_error — A File That Python Cannot Read

## Purpose
One card for every way a Python step can fail to read its text: a syntax
error, a bad indentation, an unterminated string, a null character, line
endings other than `\\n`.

## What the Extractor Does With It
A step that raises marks THAT file `error` (`transform failed: ...`) and the
run goes on with the next file; the run is unsuccessful. With
`on_error="keep"` the step never gets here: the text comes back as it is.

## The Value
The offending line, not the whole text: a card that prints a whole file is not
a card anybody reads.
"""
