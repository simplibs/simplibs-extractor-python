import ast


def first_doc_line(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Make a trailing comment out of the first line of a docstring.

    Args:
        node: A class or a function.

    Returns:
        `"  # First line"`, or an empty string if the node has no docstring.
    """

    # 1. The cleaned docstring, or nothing
    doc = ast.get_docstring(node)
    if not doc:
        return ""

    # 2. Its first non-empty line; every kind of line end counts, so a comment can never run on
    lines = doc.strip().splitlines()
    first = lines[0].strip() if lines else ""

    return f"  # {first}" if first else ""


_DESIGN_NOTES = """
# first_doc_line — A Docstring as a Comment

## Purpose
The outline keeps what a docstring says in one line, without a string that
would have to be quoted and escaped.

## `splitlines`, Not `split("\\n")`
A docstring can hold a `\\r` or a form feed written as an escape. Cut by
`\\n` only, such a character would end up in the output and `ast` would take it
for a line end, turning the rest of the comment into code.
"""
