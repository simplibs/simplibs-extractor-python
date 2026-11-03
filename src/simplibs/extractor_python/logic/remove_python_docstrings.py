from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from ._helpers import SourceOffsets, cut_statements, find_docstrings, parse_python


@validate_call
def remove_python_docstrings(text: str, *, on_error: OnError = "raise") -> str:
    """Remove the docstrings of a Python source: of the module, its classes and its functions.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged.

    Returns:
        The text without docstrings. A body left empty gets a `pass`.

    Raises:
        ParamError: The text cannot be parsed and `on_error` is `"raise"`.
    """

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut the docstring statements
    return cut_statements(text, tree, find_docstrings(tree), SourceOffsets(text))


_DESIGN_NOTES = """
# remove_python_docstrings — Documentation Out, Structure Kept

## Purpose
A step of the profiles `python/code-clean` and `python/code-no-imports`.

## What Is a Docstring
The string that is the first statement of a module, a class or a function.
Other strings, even alone on their line, are left.

## A Body Needs a Statement
`def f():` with only a docstring is `def f(): pass` afterwards; so is a class.
A module may be empty.

## Guarantee
For a text that parses, the syntax tree of the result equals the tree of the
original with the docstring statements taken out (and a `Pass` where a body
would be empty).
"""
