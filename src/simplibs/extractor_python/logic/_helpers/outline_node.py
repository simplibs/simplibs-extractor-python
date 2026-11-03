import ast
# Inners
from .collect_definitions import collect_definitions
from .first_doc_line import first_doc_line
from .format_type_params import format_type_params


def outline_node(
    node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
    depth: int,
    docstrings: bool,
) -> list[str]:
    """Write the outline of one class or function, with the definitions inside a class.

    Args:
        node: The definition.
        depth: How deeply it is indented.
        docstrings: Add the first line of the docstring as a comment.

    Returns:
        The lines of the outline; always valid Python when put together.
    """

    # 1. The decorators, as written
    pad = "    " * depth
    lines = [f"{pad}@{ast.unparse(decorator)}" for decorator in node.decorator_list]
    note = first_doc_line(node) if docstrings else ""
    params = format_type_params(node)

    # 2. A function: its signature, no body
    if not isinstance(node, ast.ClassDef):
        keyword = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        lines.append(f"{pad}{keyword} {node.name}{params}({ast.unparse(node.args)}){returns}: ...{note}")
        return lines

    # 3. A class: its bases and keywords (`metaclass=M`, `**options`)
    bases = [ast.unparse(base) for base in node.bases]
    bases += [
        f"{keyword.arg}={ast.unparse(keyword.value)}" if keyword.arg else f"**{ast.unparse(keyword.value)}"
        for keyword in node.keywords
    ]
    head = f"class {node.name}{params}" + (f"({', '.join(bases)})" if bases else "")

    # 4. The members are listed under it; a class with none is one line
    members = collect_definitions(node.body)
    if not members:
        lines.append(f"{pad}{head}: ...{note}")
        return lines
    lines.append(f"{pad}{head}:{note}")
    for member in members:
        lines.extend(outline_node(member, depth + 1, docstrings))

    return lines


_DESIGN_NOTES = """
# outline_node — One Definition Without Its Body

## Purpose
The signature of a class or a function, written by `ast.unparse` from the
parsed tree, so a default value, an annotation or a keyword is always what the
source says and never a guess of a regex.

## Always Valid Python
`def f(...): ...` and `class C: ...` are complete statements; a class with
members is a header followed by an indented block of members. The docstring
note is a comment, which cannot break anything.

## The Keywords of a Class
`class A(B, metaclass=M, **options)`: a keyword without a name is `**options`.
"""
