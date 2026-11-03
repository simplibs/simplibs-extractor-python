import ast


def find_docstrings(tree: ast.Module) -> set[ast.stmt]:
    """Find the docstring statements of a module, its classes and its functions.

    Args:
        tree: The parsed module.

    Returns:
        The `Expr` statements that are docstrings.
    """

    # 1. A docstring is a string constant that is the FIRST statement of a module, class or function
    found: set[ast.stmt] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.body:
            continue
        first = node.body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            found.add(first)

    return found


_DESIGN_NOTES = """
# find_docstrings — What Python Itself Calls a Docstring

## Purpose
The same rule as `ast.get_docstring`, applied to the whole tree at once.

## Only the First Statement
A string in the middle of a body is an expression nobody uses, not a
docstring, and stays. An f-string is not a docstring either (it is built at
run time), and stays.

## A Statement, Not a Line
A docstring may share its line (`def f(): '''doc'''`) or be wrapped in
parentheses; the statement's own span covers both.
"""
