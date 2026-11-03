import ast
from collections.abc import Sequence


_DEFINITIONS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
_BLOCK_FIELDS = ("body", "handlers", "orelse", "finalbody", "cases")
_CLAUSES = (ast.ExceptHandler, ast.match_case)


def collect_definitions(body: Sequence[ast.stmt]) -> list[ast.stmt]:
    """Collect the classes and functions defined in a body, in source order.

    Args:
        body: The statements of a module or of a class.

    Returns:
        The definitions at this level, including those inside `if`, `try`, `with`, `for`,
        `while` and `match` blocks, which are looked through but not reported.
    """

    # 1. A definition counts; a block that holds definitions is looked through
    found: list[ast.stmt] = []
    for statement in body:
        if isinstance(statement, _DEFINITIONS):
            found.append(statement)
            continue
        for field in _BLOCK_FIELDS:
            inner = getattr(statement, field, None)
            if not isinstance(inner, list):
                continue
            for item in inner:
                # 2. An `except` handler and a `case` hold a body of their own; anything else is a statement
                found.extend(collect_definitions(item.body if isinstance(item, _CLAUSES) else [item]))

    return found


_DESIGN_NOTES = """
# collect_definitions — What a Body Defines

## Purpose
The outline lists classes and functions. Which ones belong to a module or a
class is answered here.

## Looked Through, Not Entered
A function defined inside another function is a detail of that function and is
not listed. A definition under `if sys.version_info >= ...:`, inside a `try`
or under a `case` of a `match` IS a member of the module, so those blocks are
looked through. The condition is lost; if both branches define `f`, both are
listed (valid Python, which allows a redefinition).

## Clauses With a Body of Their Own
An `except` handler and a `case` are not statements: each holds a body of its
own and is looked into through it. Every other item of a block is a statement
and is looked at as one. That is all there is, so there is no third kind to
skip.

## Source Order
Definitions come in the order they stand in the file, also across blocks.
"""
