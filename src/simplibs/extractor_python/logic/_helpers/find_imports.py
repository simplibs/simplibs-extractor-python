import ast


def find_imports(tree: ast.Module) -> set[ast.stmt]:
    """Find every import statement of a module, at any depth.

    Args:
        tree: The parsed module.

    Returns:
        The `Import` and `ImportFrom` statements: at the top, inside functions and classes,
        in `try` and `if` blocks.
    """

    # 1. Both kinds, wherever they stand
    return {node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))}


_DESIGN_NOTES = """
# find_imports — Every Import, Not Only the Top Ones

## Purpose
`remove_python_imports` takes out what this finds.

## Depth
`try: import ujson / except ImportError: import json`, `if TYPE_CHECKING:` and
imports inside a function are all imports. Leaving the nested ones would leave
a file that still names its dependencies.

## `from __future__`
It is an `ImportFrom` and goes with the rest. For reading the code, a
`from __future__ import annotations` carries no information.
"""
