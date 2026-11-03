import ast
import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.presets import PYTHON_CLEAN

SOURCE = (
    '"""Module doc."""\n'
    "import os\n"
    "\n"
    "\n"
    "def f(a):\n"
    '    """Doc."""\n'
    "    # note\n"
    "    return os.getcwd() + a  # tail\n"
)


def _body(text: str) -> str:
    """The text without the line breaks around it: the preset may or may not keep the final one."""
    return text.strip("\n")


def test_is_an_action() -> None:
    assert isinstance(PYTHON_CLEAN, Action)


def test_the_errors_of_the_first_steps_come_through(subtests) -> None:
    assert_action(
        subtests,
        PYTHON_CLEAN,
        invalid_values=[5, None, "x = (\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        deep_check=False,
        verbose=False,
    )


def test_comments_and_docstrings_go_and_the_imports_stay() -> None:
    result = PYTHON_CLEAN(SOURCE)
    assert "#" not in result
    assert "Doc" not in result
    assert "import os" in result
    assert _body(result) == "import os\n\ndef f(a):\n    return os.getcwd() + a"


def test_the_syntax_tree_is_the_original_without_its_docstrings() -> None:
    tree = ast.parse(SOURCE)
    tree.body = tree.body[1:]                      # the module docstring
    tree.body[1].body = tree.body[1].body[1:]      # the docstring of `f`
    assert ast.dump(ast.parse(PYTHON_CLEAN(SOURCE))) == ast.dump(tree)


def test_a_run_of_blank_lines_becomes_one_blank_line_not_none() -> None:
    result = PYTHON_CLEAN("x = 1\n\n\n\n# c\n\n\ny = 2\n")
    assert "\n\n\n" not in result
    assert "x = 1\n\ny = 2" in result


def test_the_code_stays_in_paragraphs() -> None:
    result = PYTHON_CLEAN("def a():\n    return 1\n\n\ndef b():\n    return 2\n")
    assert "return 1\n\ndef b()" in result


def test_a_text_that_needs_nothing_stays_as_it_is() -> None:
    text = "def f(a):\n    return a\n"
    assert _body(PYTHON_CLEAN(text)) == _body(text)


def test_an_empty_text_stays_empty() -> None:
    assert PYTHON_CLEAN("").strip() == ""


@pytest.mark.parametrize("text", [SOURCE, "x = 1  # c\n\n\n\ny = 2\n", "def f():\n    '''Doc.'''\n"])
def test_a_second_run_changes_nothing(text) -> None:
    once = PYTHON_CLEAN(text)
    assert PYTHON_CLEAN(once) == once


def test_a_hash_inside_a_string_is_kept() -> None:
    assert 'x = "a # b"' in PYTHON_CLEAN('x = "a # b"  # real\n')
