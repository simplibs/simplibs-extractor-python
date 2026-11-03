from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from ._helpers import collect_definitions, outline_node, parse_python


@validate_call
def python_outline(text: str, *, docstrings: bool = True, on_error: OnError = "raise") -> str:
    """Write an overview of a Python source: its classes and functions as signatures without bodies.

    Args:
        text: The Python source.
        docstrings: Add the first line of each docstring as a trailing comment.
        on_error: `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged
            (the whole file, not an outline).

    Returns:
        The outline, valid Python; an empty string for a file that defines no class or function.

    Raises:
        ParamError: The text cannot be parsed and `on_error` is `"raise"`.

    Example:
        python_outline("@dec\\nclass A(B):\\n    def m(self, a: int = 1) -> str:\\n        return ''\\n")
        # '@dec\\nclass A(B):\\n    def m(self, a: int=1) -> str: ...\\n'
    """

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. The outline of every definition of the module
    lines: list[str] = []
    for definition in collect_definitions(tree.body):
        lines.extend(outline_node(definition, 0, docstrings))

    return "\n".join(lines) + "\n" if lines else ""


_DESIGN_NOTES = """
# python_outline — The Shape of a Module in a Few Lines

## Purpose
The step of the profile `python/outline`: what a file offers, without how it
does it. For giving a large project to a reader with a limited window, the
signatures are most of what is needed to ask the right questions.

## What Is Listed
Classes and functions of the module, methods and nested classes of a class,
looking through `if`, `try` and `with` blocks. A function inside a function is
not listed: it is the function's own detail.

## Written From the Tree
Signatures come from `ast.unparse`, not from the source text, so spacing and
line breaks are normalized (`a: int = 1` is written `a: int=1`) and the output
is always valid Python.

## Docstring as a Comment
`# First line of the docstring` after the signature. No string means nothing
to quote, escape or close.
"""
