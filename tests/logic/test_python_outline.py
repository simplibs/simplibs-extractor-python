import ast
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import python_outline


def test_the_example_of_the_docstring() -> None:
    text = "@dec\nclass A(B):\n    def m(self, a: int = 1) -> str:\n        return ''\n"
    assert python_outline(text) == "@dec\nclass A(B):\n    def m(self, a: int=1) -> str: ...\n"


def test_definitions_follow_each_other_without_blank_lines() -> None:
    assert python_outline("def a(): ...\n\n\nclass B: ...\n\n\nasync def c(): ...\n") == (
        "def a(): ...\nclass B: ...\nasync def c(): ...\n"
    )


def test_the_outline_ends_with_one_newline() -> None:
    result = python_outline("def a(): ...\n")
    assert result.endswith("\n") and not result.endswith("\n\n")


@pytest.mark.parametrize(
    "text",
    ["", "x = 1\n", "import os\nx = 1\n", "# only a comment\n", '"""Only a docstring."""\n'],
    ids=["empty", "assignment", "import", "comment", "docstring"],
)
def test_a_file_that_defines_nothing_gives_an_empty_string(text) -> None:
    assert python_outline(text) == ""


def test_the_bodies_are_gone() -> None:
    result = python_outline("def f(a):\n    secret = a * 2\n    return secret\n")
    assert "secret" not in result
    assert result == "def f(a): ...\n"


def test_the_imports_and_the_assignments_between_the_definitions_are_gone() -> None:
    assert python_outline("import os\nX = 1\ndef f(): ...\nY = 2\n") == "def f(): ...\n"


# ---------------------------------------------------------------- the first line of the docstring

def test_the_first_line_of_a_docstring_is_a_comment() -> None:
    text = 'def f():\n    """Do it.\n\n    More.\n    """\n'
    assert python_outline(text) == "def f(): ...  # Do it.\n"


def test_the_docstrings_are_on_by_default() -> None:
    assert python_outline('def f():\n    """Do it."""\n') == python_outline('def f():\n    """Do it."""\n', docstrings=True)


def test_the_docstrings_can_be_switched_off() -> None:
    assert python_outline('def f():\n    """Do it."""\n', docstrings=False) == "def f(): ...\n"


def test_a_class_and_its_methods_with_docstrings() -> None:
    text = 'class A:\n    """The class."""\n    def m(self):\n        """Do it."""\n'
    assert python_outline(text) == "class A:  # The class.\n    def m(self): ...  # Do it.\n"
    assert python_outline(text, docstrings=False) == "class A:\n    def m(self): ...\n"


def test_the_module_docstring_is_not_part_of_the_outline() -> None:
    assert python_outline('"""Module."""\ndef f(): ...\n') == "def f(): ...\n"


# ---------------------------------------------------------------- what is listed

def test_methods_and_nested_classes_are_listed_under_their_class() -> None:
    text = "class A:\n    class B:\n        def m(self): ...\n    def n(self): ...\n"
    assert python_outline(text) == "class A:\n    class B:\n        def m(self): ...\n    def n(self): ...\n"


def test_a_function_inside_a_function_is_not_listed() -> None:
    assert python_outline("def f():\n    def g(): ...\n") == "def f(): ...\n"


@pytest.mark.parametrize(
    "text",
    [
        "if x:\n    def f(): ...\n",
        "try:\n    def f(): ...\nexcept E:\n    pass\n",
        "with a:\n    def f(): ...\n",
        "for i in x:\n    def f(): ...\n",
    ],
    ids=["if", "try", "with", "for"],
)
def test_a_definition_inside_a_block_is_listed(text) -> None:
    assert python_outline(text) == "def f(): ...\n"


def test_the_decorators_are_kept() -> None:
    text = "@dataclass(frozen=True)\nclass A:\n    @property\n    def p(self) -> int: ...\n"
    assert python_outline(text) == "@dataclass(frozen=True)\nclass A:\n    @property\n    def p(self) -> int: ...\n"


# ---------------------------------------------------------------- written from the tree

def test_the_spacing_and_the_line_breaks_are_normalized() -> None:
    assert python_outline("def f(\n    a,\n    b = 2,\n):\n    ...\n") == "def f(a, b=2): ...\n"


def test_strings_are_written_the_way_unparse_writes_them() -> None:
    assert python_outline('def f(a="č"): ...\n') == "def f(a='č'): ...\n"


def test_wide_characters_in_names_and_defaults() -> None:
    assert python_outline("def čau(a='😀'): ...\n") == "def čau(a='😀'): ...\n"


@pytest.mark.parametrize(
    "text",
    [
        "def f(a, b=1): ...\n",
        'class A(B, metaclass=M):\n    """Doc."""\n    @property\n    def p(self) -> int: ...\n    class N:\n        def x(self): ...\n',
        "@dec\nasync def f(a: int = 1) -> str: ...\n",
        "if x:\n    def f(): ...\n",
    ],
)
@pytest.mark.parametrize("docstrings", [True, False])
def test_the_outline_is_valid_python(text, docstrings) -> None:
    ast.parse(python_outline(text, docstrings=docstrings))


def test_the_outline_of_an_outline_is_itself() -> None:
    text = "@dec\nclass A(B):\n    def m(self, a: int = 1) -> str:\n        return ''\n\ndef f(x): ...\n"
    once = python_outline(text, docstrings=False)
    assert python_outline(once, docstrings=False) == once


# ---------------------------------------------------------------- a text that cannot be read

def test_a_text_that_does_not_parse_is_a_card() -> None:
    with pytest.raises(ParamError):
        python_outline("def f(:\n")


def test_a_text_that_does_not_parse_with_keep_gives_the_whole_text_back() -> None:
    """The text, not an outline: nothing is guessed about a file that cannot be read."""
    text = "def f(:\n    pass\n"
    assert python_outline(text, on_error="keep") == text


@pytest.mark.parametrize("text", ["def f(): ...\r\n", "def f(): ...\r"])
def test_other_line_endings_are_a_card_or_the_same_text(text) -> None:
    with pytest.raises(ParamError):
        python_outline(text)
    assert python_outline(text, on_error="keep") == text


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        python_outline("x = (\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"def f(): ...", ["def f(): ..."]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        python_outline(value)


@pytest.mark.parametrize("value", ["yes", None, 1, "False"])
def test_docstrings_must_be_a_bool(value) -> None:
    with pytest.raises(ValidationError):
        python_outline("def f(): ...\n", docstrings=value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        python_outline("x = 1\n", on_error=value)


def test_the_options_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        python_outline("x = 1\n", False)  # type: ignore[misc]
    with pytest.raises(TypeError):
        python_outline("x = 1\n", True, "keep")  # type: ignore[misc]
