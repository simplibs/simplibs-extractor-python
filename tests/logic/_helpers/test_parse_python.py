import ast
import pytest
from simplibs.exception import ParamError
from simplibs.extractor_python.logic._helpers import parse_python


def test_returns_the_syntax_tree() -> None:
    text = "def f(a):\n    return a\n"
    tree = parse_python(text, "raise")
    assert isinstance(tree, ast.Module)
    assert ast.dump(tree) == ast.dump(ast.parse(text))


def test_an_empty_text_is_an_empty_module() -> None:
    tree = parse_python("", "raise")
    assert isinstance(tree, ast.Module)
    assert tree.body == []


@pytest.mark.parametrize("on_error", ["raise", "keep"])
def test_a_valid_text_gives_a_tree_in_both_modes(on_error) -> None:
    assert isinstance(parse_python("x = 1\n", on_error), ast.Module)


@pytest.mark.parametrize(
    "text",
    ["x = (\n", "print 'old'\n", "def f(:\n", "if x:\nprint(1)\n", "x = 1\0"],
    ids=["open-bracket", "python-2", "bad-signature", "no-indent", "null-byte"],
)
def test_a_text_that_is_not_python_is_a_card(text) -> None:
    with pytest.raises(ParamError):
        parse_python(text, "raise")


@pytest.mark.parametrize(
    "text",
    ["x = (\n", "print 'old'\n", "def f(:\n", "if x:\nprint(1)\n", "x = 1\0"],
    ids=["open-bracket", "python-2", "bad-signature", "no-indent", "null-byte"],
)
def test_a_text_that_is_not_python_gives_none_with_keep(text) -> None:
    assert parse_python(text, "keep") is None


@pytest.mark.parametrize("text", ["x = 1\r\n", "x = 1\r"])
def test_other_line_endings_are_refused(text) -> None:
    with pytest.raises(ParamError):
        parse_python(text, "raise")
    assert parse_python(text, "keep") is None
