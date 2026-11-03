import ast
import tokenize
import pytest
from simplibs.extractor_python.logic._helpers import describe_source_failure


def test_a_syntax_error_gives_its_message_and_its_line() -> None:
    assert describe_source_failure(SyntaxError("bad thing", ("<s>", 4, 2, "text"))) == ("bad thing", 4)


def test_a_syntax_error_without_a_message_says_invalid_syntax() -> None:
    assert describe_source_failure(SyntaxError()) == ("invalid syntax", None)


def test_the_syntax_error_of_a_real_parse() -> None:
    with pytest.raises(SyntaxError) as info:
        ast.parse("x = 1\ny = (\n")
    reason, line = describe_source_failure(info.value)
    assert isinstance(reason, str) and reason != ""
    assert isinstance(line, int) and line >= 1


def test_an_indentation_error_is_a_syntax_error() -> None:
    with pytest.raises(IndentationError) as info:
        ast.parse("def f():\nx = 1\n")
    reason, line = describe_source_failure(info.value)
    assert reason != ""
    assert line == 2


def test_a_token_error_gives_its_message_and_the_line_of_its_position() -> None:
    assert describe_source_failure(tokenize.TokenError("EOF in multi-line string", (5, 0))) == (
        "EOF in multi-line string",
        5,
    )


def test_a_token_error_without_arguments() -> None:
    assert describe_source_failure(tokenize.TokenError()) == ("tokenizing failed", None)


def test_a_token_error_without_a_position() -> None:
    assert describe_source_failure(tokenize.TokenError("lonely")) == ("lonely", None)


@pytest.mark.parametrize("position", ["not a tuple", 7, None])
def test_a_token_error_with_a_position_that_is_no_tuple_has_no_line(position) -> None:
    assert describe_source_failure(tokenize.TokenError("msg", position)) == ("msg", None)


def test_any_other_error_gives_its_text_and_no_line() -> None:
    assert describe_source_failure(ValueError("boom")) == ("boom", None)


@pytest.mark.parametrize("error", [ValueError(), RecursionError(), KeyError()])
def test_an_error_without_a_text_gives_its_class_name(error) -> None:
    reason, line = describe_source_failure(error)
    assert reason == type(error).__name__ or reason == str(error)
    assert reason != ""
    assert line is None
