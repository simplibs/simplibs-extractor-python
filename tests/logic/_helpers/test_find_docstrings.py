import ast
import pytest
from simplibs.extractor_python.logic._helpers import find_docstrings


def _found(source: str) -> list[str]:
    """The strings of the docstrings that were found, sorted."""
    return sorted(node.value.value for node in find_docstrings(ast.parse(source)))


def test_returns_a_set_of_expression_statements() -> None:
    found = find_docstrings(ast.parse('"""Doc."""\n'))
    assert isinstance(found, set)
    assert all(isinstance(node, ast.Expr) for node in found)


def test_an_empty_module_has_none() -> None:
    assert find_docstrings(ast.parse("")) == set()


def test_the_docstring_of_a_module() -> None:
    assert _found('"""Module."""\nx = 1\n') == ["Module."]


def test_the_docstring_of_a_function_an_async_function_and_a_class() -> None:
    source = 'def f():\n    """F."""\nasync def g():\n    """G."""\nclass A:\n    """A."""\n'
    assert _found(source) == ["A.", "F.", "G."]


def test_the_docstrings_of_methods_and_nested_definitions() -> None:
    source = 'class A:\n    """A."""\n    def m(self):\n        """M."""\n        def inner():\n            """I."""\n'
    assert _found(source) == ["A.", "I.", "M."]


def test_all_the_levels_together() -> None:
    source = '"""Module."""\ndef f():\n    """F."""\n'
    assert _found(source) == ["F.", "Module."]


@pytest.mark.parametrize(
    "source",
    [
        "def f():\n    x = 1\n    'not first'\n",
        "def f():\n    1\n",
        "def f():\n    b'bytes'\n",
        'def f():\n    f"x{1}"\n',
        "def f():\n    pass\n",
        "if x:\n    'in a block'\n",
        "x = 1\n'after a statement'\n",
        "for i in x:\n    'in a loop'\n",
    ],
    ids=["not-first", "number", "bytes", "f-string", "no-string", "in-if", "module-not-first", "in-loop"],
)
def test_only_a_string_that_is_the_first_statement_of_a_definition_counts(source) -> None:
    assert _found(source) == []


def test_two_strings_in_a_row_make_one_docstring_and_one_plain_string() -> None:
    assert _found("def f():\n    'one'\n    'two'\n") == ["one"]


def test_an_implicit_concatenation_is_one_docstring() -> None:
    assert _found('def f():\n    "a" "b"\n') == ["ab"]


def test_a_definition_with_a_docstring_and_a_body() -> None:
    assert _found('def f():\n    """Doc."""\n    return 1\n') == ["Doc."]
