import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.presets import PYTHON_NO_IMPORTS

SOURCE = (
    "import os\n"
    "from a import b\n"
    "\n"
    "@dec\n"
    "def f(a):\n"
    '    """Doc."""\n'
    "\n"
    "    # c\n"
    "    return a  # tail\n"
)


def _body(text: str) -> str:
    """The text without the line breaks around it: the preset may or may not keep the final one."""
    return text.strip("\n")


def test_is_an_action() -> None:
    assert isinstance(PYTHON_NO_IMPORTS, Action)


def test_the_errors_of_the_first_steps_come_through(subtests) -> None:
    assert_action(
        subtests,
        PYTHON_NO_IMPORTS,
        invalid_values=[5, None, "x = (\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        deep_check=False,
        verbose=False,
    )


def test_only_the_logic_is_left() -> None:
    assert _body(PYTHON_NO_IMPORTS(SOURCE)) == "def f(a):\n    return a"


def test_nothing_of_the_wiring_is_left() -> None:
    result = PYTHON_NO_IMPORTS(SOURCE)
    assert "import" not in result
    assert "@" not in result
    assert "#" not in result
    assert "Doc" not in result


def test_there_are_no_blank_lines_at_all() -> None:
    result = PYTHON_NO_IMPORTS("import os\n\n\nx = 1\n\n\n\ny = 2\n")
    assert "\n\n" not in result.strip("\n")
    assert _body(result) == "x = 1\ny = 2"


def test_a_class_keeps_its_methods() -> None:
    text = 'import os\n\nclass A:\n    """Doc."""\n\n    @property\n    def p(self):\n        return 1\n'
    assert _body(PYTHON_NO_IMPORTS(text)) == "class A:\n    def p(self):\n        return 1"


def test_a_function_that_had_only_a_docstring_gets_a_pass() -> None:
    assert _body(PYTHON_NO_IMPORTS('def f():\n    """Only."""\n')) == "def f():\n    pass"


def test_a_block_that_had_only_an_import_gets_a_pass() -> None:
    assert _body(PYTHON_NO_IMPORTS("try:\n    import a\nexcept ImportError:\n    pass\n")) == (
        "try:\n    pass\nexcept ImportError:\n    pass"
    )


def test_blank_lines_inside_a_multi_line_string_go_too() -> None:
    """Known and written down in the design notes: `COMPACT` does not know about strings."""
    assert _body(PYTHON_NO_IMPORTS('x = """a\n\nb"""\n')) == 'x = """a\nb"""'


@pytest.mark.parametrize("text", [SOURCE, "import a\n\n\nx = 1  # c\n", "@dec\nclass A:\n    '''Doc.'''\n"])
def test_a_second_run_changes_nothing(text) -> None:
    once = PYTHON_NO_IMPORTS(text)
    assert PYTHON_NO_IMPORTS(once) == once


def test_an_empty_text_stays_empty() -> None:
    assert PYTHON_NO_IMPORTS("").strip() == ""
