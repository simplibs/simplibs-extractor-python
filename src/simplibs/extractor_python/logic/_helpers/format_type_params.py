import ast


def format_type_params(node: ast.AST) -> str:
    """Write the type parameters of a class or function (`def f[T](x: T)`, Python 3.12+).

    Args:
        node: A class or a function definition.

    Returns:
        `"[T, U: int]"`, or an empty string if there are none (and always on older Pythons).
    """

    # 1. `type_params` exists since Python 3.12; before that there is nothing to write
    params = getattr(node, "type_params", None)
    if not params:
        return ""

    return "[" + ", ".join(ast.unparse(param) for param in params) + "]"


_DESIGN_NOTES = """
# format_type_params — The Brackets After the Name

## Purpose
`class Box[T]:` and `def first[T](items: list[T]) -> T:` carry their type
parameters in a field that older Pythons do not have. Without them the outline
would name a different signature than the source.
"""
