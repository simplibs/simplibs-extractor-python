import ast
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import remove_python_docstrings

SAMPLES = [
    '"""Module."""\nx = 1\n',
    'def f():\n    """Doc."""\n    return 1\n',
    'def f():\n    """Only a docstring."""\n',
    'class A:\n    """The class."""\n    def m(self):\n        """The method."""\n        return 1\n',
    'class A:\n    """Only a docstring."""\n',
    'async def f():\n    """Doc."""\n',
    'def f():\n    """First.\n\n    Second.\n    """\n    return 1\n',
    "def f():\n    'one'\n    'two'\n    return 1\n",
    'def f(): "doc"; return 1\n',
    'def outer():\n    """O."""\n    def inner():\n        """I."""\n    return inner\n',
    'x = "č€😀"\ndef f():\n    """Doc."""\n',
]


def _without_docstrings(tree: ast.Module) -> str:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                node.body = node.body[1:] or ([] if isinstance(node, ast.Module) else [ast.Pass()])
    return ast.dump(tree)


@pytest.mark.parametrize(
    "text, expected",
    [
        ('"""Module."""\nx = 1\n', "x = 1\n"),
        ('def f():\n    """Doc."""\n    return 1\n', "def f():\n    return 1\n"),
        ('class A:\n    """Doc."""\n    x = 1\n', "class A:\n    x = 1\n"),
        ('async def f():\n    """Doc."""\n    return 1\n', "async def f():\n    return 1\n"),
        ('def f():\n    """First.\n\n    Second.\n    """\n    return 1\n', "def f():\n    return 1\n"),
        ('def f(): "doc"; return 1\n', "def f(): return 1\n"),
        ("def f():\n    'one'\n    'two'\n    return 1\n", "def f():\n    'two'\n    return 1\n"),
        ('x = "č€😀"\ndef f():\n    """Doc."""\n    return 1\n', 'x = "č€😀"\ndef f():\n    return 1\n'),
    ],
    ids=["module", "function", "class", "async", "several-lines", "semicolon", "only-the-first-string", "wide-characters"],
)
def test_the_docstring_goes_and_the_rest_stays(text, expected) -> None:
    assert remove_python_docstrings(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ('def f():\n    """Only a docstring."""\n', "def f():\n    pass\n"),
        ('class A:\n    """Only a docstring."""\n', "class A:\n    pass\n"),
        ('async def f():\n    """Only a docstring."""\n', "async def f():\n    pass\n"),
        ('class A:\n    def m(self):\n        """Doc."""\n', "class A:\n    def m(self):\n        pass\n"),
    ],
    ids=["function", "class", "async", "method"],
)
def test_a_body_left_empty_gets_a_pass(text, expected) -> None:
    assert remove_python_docstrings(text) == expected


def test_a_module_may_end_up_empty() -> None:
    assert remove_python_docstrings('"""Only a docstring."""\n') == ""


def test_the_docstrings_of_every_level_go_together() -> None:
    text = 'def outer():\n    """O."""\n    def inner():\n        """I."""\n    return inner\n'
    assert remove_python_docstrings(text) == "def outer():\n    def inner():\n        pass\n    return inner\n"


@pytest.mark.parametrize(
    "text",
    [
        "x = 1\n'after a statement'\n",
        "def f():\n    x = 1\n    'not first'\n",
        "def f():\n    f'{1}'\n",
        "def f():\n    b'bytes'\n",
        "def f():\n    1\n",
        "if x:\n    'in a block'\n",
    ],
    ids=["module-not-first", "function-not-first", "f-string", "bytes", "number", "in-if"],
)
def test_a_string_that_is_not_a_docstring_is_left(text) -> None:
    assert remove_python_docstrings(text) == text


def test_a_text_without_docstrings_stays_as_it_is() -> None:
    text = "def f(a,b):\n    return  a+b\n"
    assert remove_python_docstrings(text) == text


def test_an_empty_text_stays_empty() -> None:
    assert remove_python_docstrings("") == ""


# ---------------------------------------------------------------- the guarantees of the design notes

@pytest.mark.parametrize("text", SAMPLES)
def test_the_tree_is_the_original_without_the_docstrings_and_with_a_pass_where_a_body_would_be_empty(text) -> None:
    result = remove_python_docstrings(text)
    assert ast.dump(ast.parse(result)) == _without_docstrings(ast.parse(text))


@pytest.mark.parametrize("text", SAMPLES)
def test_a_second_run_removes_nothing_that_the_first_left(text) -> None:
    """A string that became the first statement is a docstring now; the tree rule is applied once more."""
    once = remove_python_docstrings(text)
    twice = remove_python_docstrings(once)
    assert ast.dump(ast.parse(twice)) == _without_docstrings(ast.parse(once))


# ---------------------------------------------------------------- a text that cannot be read

def test_a_text_that_does_not_parse_is_a_card() -> None:
    with pytest.raises(ParamError):
        remove_python_docstrings('def f(:\n    """Doc."""\n')


def test_a_text_that_does_not_parse_with_keep_gives_the_text_back() -> None:
    text = 'def f(:\n    """Doc."""\n'
    assert remove_python_docstrings(text, on_error="keep") == text


@pytest.mark.parametrize("text", ['def f():\r\n    """Doc."""\r\n', 'def f():\r    """Doc."""\r'])
def test_other_line_endings_are_a_card_or_the_same_text(text) -> None:
    with pytest.raises(ParamError):
        remove_python_docstrings(text)
    assert remove_python_docstrings(text, on_error="keep") == text


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        remove_python_docstrings("def f(:\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"x = 1", ["x = 1"]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_docstrings(value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_docstrings("x = 1\n", on_error=value)


def test_on_error_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        remove_python_docstrings("x = 1\n", "keep")  # type: ignore[misc]
