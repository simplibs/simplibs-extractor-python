from simplibs.validate import validate_call
# Outers
from ..annotations import OnError
# Inners
from ._helpers import SourceOffsets, cut_statements, find_imports, parse_python


@validate_call
def remove_python_imports(text: str, *, on_error: OnError = "raise") -> str:
    """Remove the import statements of a Python source, at any depth.

    Args:
        text: The Python source.
        on_error: `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged.

    Returns:
        The text without imports. A body left empty gets a `pass`; `import a; x = 1` keeps `x = 1`.

    Raises:
        ParamError: The text cannot be parsed and `on_error` is `"raise"`.
    """

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut the import statements
    return cut_statements(text, tree, find_imports(tree), SourceOffsets(text))


_DESIGN_NOTES = """
# remove_python_imports — The Logic Without Its Dependencies

## Purpose
A step of the profile `python/code-no-imports`.

## Guarantee
For a text that parses, the syntax tree of the result equals the tree of the
original without the `Import` and `ImportFrom` statements (and a `Pass` where a
body would be empty).

## What Is Left Behind
Names that were imported are still used further down; the reader of the
output sees code that refers to `Path` or `np` without the line that says
where they come from. That is what the profile is for: the logic, not the
wiring.
"""
