import ast
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import remove_python_imports

SAMPLES = [
    "import os\nx = 1\n",
    "import os\n",
    "from a import b\nfrom . import c\nfrom ..d import e as f\nx = 1\n",
    "from __future__ import annotations\nx = 1\n",
    "from a import (\n    b,\n    c,\n)\nx = 1\n",
    "import a; x = 1\n",
    "x = 1; import a\n",
    "def f():\n    import os\n    return os.name\n",
    "def f():\n    import os\n",
    "class A:\n    import os\n",
    "try:\n    import a\nexcept ImportError:\n    import b\n",
    "if TYPE_CHECKING:\n    from a import B\nx = 1\n",
    "def f(): import os; import sys\n",
    'x = "č€😀"\nimport os\n',
]


def _without_imports(tree: ast.Module) -> str:
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            statements = getattr(node, field, None)
            if not isinstance(statements, list) or not statements:
                continue
            kept = [s for s in statements if not isinstance(s, (ast.Import, ast.ImportFrom))]
            if len(kept) != len(statements):
                setattr(node, field, kept or ([] if isinstance(node, ast.Module) else [ast.Pass()]))
    return ast.dump(tree)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("import os\nx = 1\n", "x = 1\n"),
        ("from a import b\nx = 1\n", "x = 1\n"),
        ("from . import c\nfrom ..d import e as f\nx = 1\n", "x = 1\n"),
        ("from __future__ import annotations\nx = 1\n", "x = 1\n"),
        ("from a import (\n    b,\n    c,\n)\nx = 1\n", "x = 1\n"),
        ("import a; x = 1\n", "x = 1\n"),
        ("x = 1; import a\n", "x = 1\n"),
        ("x = 1; import a; y = 2\n", "x = 1; y = 2\n"),
        ("def f():\n    import os\n    return os.name\n", "def f():\n    return os.name\n"),
        ("if TYPE_CHECKING:\n    from a import B\nx = 1\n", "if TYPE_CHECKING:\n    pass\nx = 1\n"),
        ('x = "č€😀"\nimport os\ny = 2\n', 'x = "č€😀"\ny = 2\n'),
    ],
    ids=[
        "import", "from", "relative", "future", "several-lines", "semicolon-first", "semicolon-last", "semicolon-middle",
        "in-function", "type-checking", "wide-characters",
    ],
)
def test_the_imports_go_and_the_rest_stays(text, expected) -> None:
    assert remove_python_imports(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("def f():\n    import os\n", "def f():\n    pass\n"),
        ("class A:\n    import os\n", "class A:\n    pass\n"),
        ("try:\n    import a\nexcept ImportError:\n    import b\n", "try:\n    pass\nexcept ImportError:\n    pass\n"),
        ("def f(): import os; import sys\n", "def f(): pass\n"),
    ],
    ids=["function", "class", "try-except", "one-line"],
)
def test_a_body_left_empty_gets_a_pass(text, expected) -> None:
    assert remove_python_imports(text) == expected


def test_a_module_of_imports_becomes_empty() -> None:
    assert remove_python_imports("import os\nfrom a import b\n") == ""


def test_the_names_that_were_imported_are_still_used_below() -> None:
    result = remove_python_imports("from pathlib import Path\n\nx = Path('.')\n")
    assert "Path('.')" in result
    assert "import" not in result


def test_a_text_without_imports_stays_as_it_is() -> None:
    text = "def f(a,b):\n    return  a+b\n"
    assert remove_python_imports(text) == text


def test_an_empty_text_stays_empty() -> None:
    assert remove_python_imports("") == ""


@pytest.mark.parametrize("text", ["importlib = 1\n", "x = __import__('os')\n", "x = 'import os'\n", "# import os\n"])
def test_something_that_only_looks_like_an_import_is_never_touched(text) -> None:
    assert remove_python_imports(text) == text


# ---------------------------------------------------------------- the guarantees of the design notes

@pytest.mark.parametrize("text", SAMPLES)
def test_the_tree_is_the_original_without_the_imports_and_with_a_pass_where_a_body_would_be_empty(text) -> None:
    result = remove_python_imports(text)
    assert ast.dump(ast.parse(result)) == _without_imports(ast.parse(text))


@pytest.mark.parametrize("text", SAMPLES)
def test_a_second_run_changes_nothing(text) -> None:
    once = remove_python_imports(text)
    assert remove_python_imports(once) == once


@pytest.mark.parametrize("text", SAMPLES)
def test_no_import_is_left(text) -> None:
    tree = ast.parse(remove_python_imports(text))
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))


# ---------------------------------------------------------------- a text that cannot be read

def test_a_text_that_does_not_parse_is_a_card() -> None:
    with pytest.raises(ParamError):
        remove_python_imports("import os\nx = (\n")


def test_a_text_that_does_not_parse_with_keep_gives_the_text_back() -> None:
    text = "import os\nx = (\n"
    assert remove_python_imports(text, on_error="keep") == text


@pytest.mark.parametrize("text", ["import os\r\nx = 1\r\n", "import os\rx = 1\r"])
def test_other_line_endings_are_a_card_or_the_same_text(text) -> None:
    with pytest.raises(ParamError):
        remove_python_imports(text)
    assert remove_python_imports(text, on_error="keep") == text


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        remove_python_imports("x = (\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"import os", ["import os"]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_imports(value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_imports("x = 1\n", on_error=value)


def test_on_error_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        remove_python_imports("x = 1\n", "keep")  # type: ignore[misc]
