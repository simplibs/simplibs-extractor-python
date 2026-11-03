import ast
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import remove_python_decorators

SAMPLES = [
    "@dec\ndef f(): ...\n",
    "@a\n@b(1)\n@c.d\ndef f(): ...\n",
    "@(factory)\ndef f(): ...\n",
    "@dec(\n    1,\n    2,\n)\nclass A: ...\n",
    "class A:\n    @property\n    def p(self): ...\n    @staticmethod\n    def s(): ...\n",
    "def f():\n    @inner\n    def g(): ...\n    return g\n",
    "@dec\nasync def f(): ...\n",
    'x = "č€😀"\n@dec\ndef f(): ...\n',
    "x = a @ b\n@dec\ndef f(): ...\n",
]


def _without_decorators(tree: ast.Module) -> str:
    for node in ast.walk(tree):
        if hasattr(node, "decorator_list"):
            node.decorator_list = []
    return ast.dump(tree)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("@dec\ndef f(): ...\n", "def f(): ...\n"),
        ("@a\n@b(1)\n@c.d\ndef f(): ...\n", "def f(): ...\n"),
        ("@dec\nclass A: ...\n", "class A: ...\n"),
        ("@dec\nasync def f(): ...\n", "async def f(): ...\n"),
        ("@(factory)\ndef f(): ...\n", "def f(): ...\n"),
        ("@dec(\n    1,\n    2,\n)\ndef f(): ...\n", "def f(): ...\n"),
        ("class A:\n    @property\n    def p(self): ...\n", "class A:\n    def p(self): ...\n"),
        ("def f():\n    @inner\n    def g(): ...\n    return g\n", "def f():\n    def g(): ...\n    return g\n"),
        ('x = "č€😀"\n@dec\ndef f(): ...\n', 'x = "č€😀"\ndef f(): ...\n'),
    ],
    ids=["one", "three", "class", "async", "brackets", "several-lines", "method", "nested", "wide-characters"],
)
def test_the_decorators_go_with_their_lines(text, expected) -> None:
    assert remove_python_decorators(text) == expected


def test_a_text_without_decorators_stays_as_it_is() -> None:
    text = "def f(a,b):\n    return  a+b\n"
    assert remove_python_decorators(text) == text


def test_an_empty_text_stays_empty() -> None:
    assert remove_python_decorators("") == ""


@pytest.mark.parametrize(
    "text",
    ['x = "@dec"\n', "x = a @ b\n", "# @dec\ndef f(): ...\n", "def f(a):\n    return a @ a\n"],
    ids=["string", "matmul", "comment", "matmul-in-function"],
)
def test_an_at_sign_that_is_not_a_decorator_is_never_touched(text) -> None:
    assert remove_python_decorators(text) == text


# ---------------------------------------------------------------- the guarantees of the design notes

@pytest.mark.parametrize("text", SAMPLES)
def test_the_tree_is_the_original_with_every_decorator_list_emptied(text) -> None:
    result = remove_python_decorators(text)
    assert ast.dump(ast.parse(result)) == _without_decorators(ast.parse(text))


@pytest.mark.parametrize("text", SAMPLES)
def test_a_second_run_changes_nothing(text) -> None:
    once = remove_python_decorators(text)
    assert remove_python_decorators(once) == once


def test_a_comment_on_the_line_of_a_decorator_does_not_break_the_result() -> None:
    text = "@dec  # note\ndef f(): ...\n"
    assert ast.dump(ast.parse(remove_python_decorators(text))) == _without_decorators(ast.parse(text))


# ---------------------------------------------------------------- a text that cannot be read

def test_a_text_that_does_not_parse_is_a_card() -> None:
    with pytest.raises(ParamError):
        remove_python_decorators("@dec\ndef f(:\n")


def test_a_text_that_does_not_parse_with_keep_gives_the_text_back() -> None:
    text = "@dec\ndef f(:\n"
    assert remove_python_decorators(text, on_error="keep") == text


@pytest.mark.parametrize("text", ["@dec\r\ndef f(): ...\r\n", "@dec\rdef f(): ...\r"])
def test_other_line_endings_are_a_card_or_the_same_text(text) -> None:
    with pytest.raises(ParamError):
        remove_python_decorators(text)
    assert remove_python_decorators(text, on_error="keep") == text


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        remove_python_decorators("def f(:\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"x = 1", ["x = 1"]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_decorators(value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_decorators("x = 1\n", on_error=value)


def test_on_error_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        remove_python_decorators("x = 1\n", "keep")  # type: ignore[misc]
