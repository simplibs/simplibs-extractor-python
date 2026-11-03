import ast
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import remove_python_comments

SAMPLES = [
    "x = 1  # note\n",
    "# only\nx = 1\n",
    "def f():\n    # c\n    return 1\n",
    "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nx = 1\n",
    'x = "a # b"  # real\n',
    "x = [\n    1,  # one\n    2,\n]\n",
    "class A:\n    # about x\n    x = 1  # the x\n\n    def m(self):  # method\n        return self.x\n",
    "x = 1\n\n# c\n\ny = 2\n",
]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("x = 1  # note\n", "x = 1\n"),
        ("# only\nx = 1\n", "x = 1\n"),
        ("x = 1\n# between\ny = 2\n", "x = 1\ny = 2\n"),
        ("def f():\n    # c\n    return 1\n", "def f():\n    return 1\n"),
        ("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nx = 1\n", "x = 1\n"),
        ("x = [\n    1,  # one\n    2,\n]\n", "x = [\n    1,\n    2,\n]\n"),
        ("x = 1  # c", "x = 1"),
        ('x = "č€😀"  # c\ny = 2\n', 'x = "č€😀"\ny = 2\n'),
    ],
    ids=["after-code", "own-line", "between", "indented", "shebang", "in-bracket", "no-final-newline", "wide-characters"],
)
def test_the_comments_go_and_the_code_stays(text, expected) -> None:
    assert remove_python_comments(text) == expected


def test_a_text_that_holds_only_comments_becomes_empty() -> None:
    assert remove_python_comments("# a\n# b\n") == ""


def test_an_empty_text_stays_empty() -> None:
    assert remove_python_comments("") == ""


def test_a_text_without_comments_stays_as_it_is() -> None:
    text = "def f(a,b):\n    return  a+b\n"
    assert remove_python_comments(text) == text


@pytest.mark.parametrize(
    "text",
    ['x = "a # b"\n', "x = '''# not\n# a comment'''\n", 'x = """\n# no\n"""\n', "x = r'#'\n"],
    ids=["double", "triple-single", "triple-double", "raw"],
)
def test_a_hash_inside_a_string_is_never_touched(text) -> None:
    assert remove_python_comments(text) == text


def test_the_empty_lines_around_a_comment_stay() -> None:
    assert remove_python_comments("x = 1\n\n# c\n\ny = 2\n") == "x = 1\n\n\ny = 2\n"


# ---------------------------------------------------------------- the guarantees of the design notes

@pytest.mark.parametrize("text", SAMPLES)
def test_the_syntax_tree_does_not_change(text) -> None:
    assert ast.dump(ast.parse(remove_python_comments(text))) == ast.dump(ast.parse(text))


@pytest.mark.parametrize("text", SAMPLES)
def test_a_second_run_changes_nothing(text) -> None:
    once = remove_python_comments(text)
    assert remove_python_comments(once) == once


@pytest.mark.parametrize("text", SAMPLES)
def test_no_comment_is_left(text) -> None:
    assert "#" not in remove_python_comments(text).replace('"a # b"', "")


def test_a_text_that_ast_refuses_but_the_tokenizer_reads_still_loses_its_comments() -> None:
    assert remove_python_comments("x = = 1  # c\n") == "x = = 1\n"


# ---------------------------------------------------------------- a text that cannot be read

def test_an_unclosed_bracket_is_a_card() -> None:
    with pytest.raises(ParamError):
        remove_python_comments("x = (\n# c\n")


def test_an_unclosed_bracket_with_keep_gives_the_text_back() -> None:
    text = "x = (\n# c\n"
    assert remove_python_comments(text, on_error="keep") == text


@pytest.mark.parametrize("text", ["x = 1  # c\r\n", "x = 1  # c\r"])
def test_other_line_endings_are_a_card_or_the_same_text(text) -> None:
    with pytest.raises(ParamError):
        remove_python_comments(text)
    assert remove_python_comments(text, on_error="keep") == text


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        remove_python_comments("x = (\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"x = 1", ["x = 1"]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_comments(value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        remove_python_comments("x = 1\n", on_error=value)


def test_on_error_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        remove_python_comments("x = 1\n", "keep")  # type: ignore[misc]
