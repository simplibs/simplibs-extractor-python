import ast
import pytest
from simplibs.extractor_python.logic._helpers import find_imports


def _lines(source: str) -> list[int]:
    return sorted(node.lineno for node in find_imports(ast.parse(source)))


def test_returns_a_set_of_statements() -> None:
    found = find_imports(ast.parse("import os\n"))
    assert isinstance(found, set)
    assert all(isinstance(node, (ast.Import, ast.ImportFrom)) for node in found)


def test_a_text_without_imports_has_none() -> None:
    assert find_imports(ast.parse("x = 1\ndef f(): ...\n")) == set()
    assert find_imports(ast.parse("")) == set()


def test_both_kinds_at_the_top() -> None:
    assert _lines("import os\nfrom a import b\nimport c.d as e\n") == [1, 2, 3]


def test_a_relative_import_and_a_future_import() -> None:
    assert _lines("from __future__ import annotations\nfrom . import x\nfrom ..a import b\n") == [1, 2, 3]


@pytest.mark.parametrize(
    "source",
    [
        "def f():\n    import a\n",
        "class A:\n    import a\n",
        "if x:\n    import a\n",
        "if x:\n    pass\nelse:\n    import a\n",
        "try:\n    import a\nexcept ImportError:\n    pass\n",
        "try:\n    pass\nexcept ImportError:\n    import a\n",
        "with x:\n    import a\n",
        "def f():\n    def g():\n        import a\n",
    ],
    ids=["function", "class", "if", "else", "try", "except", "with", "nested-function"],
)
def test_an_import_is_found_at_any_depth(source) -> None:
    assert len(find_imports(ast.parse(source))) == 1


def test_the_statements_are_the_ones_of_the_tree() -> None:
    tree = ast.parse("import os\n")
    assert find_imports(tree) == {tree.body[0]}


def test_a_name_that_only_looks_like_an_import_is_not_one() -> None:
    assert find_imports(ast.parse("importlib = 1\n__import__('os')\n")) == set()
