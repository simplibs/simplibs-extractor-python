import ast
import tokenize
import pytest
from simplibs.exception import ParamError
from simplibs.extractor_python.logic._helpers import guarded_parse


def test_returns_what_the_parser_returned() -> None:
    assert guarded_parse("abc", "raise", str.upper) == "ABC"
    assert isinstance(guarded_parse("x = 1\n", "raise", ast.parse), ast.Module)


@pytest.mark.parametrize("on_error", ["raise", "keep"])
def test_a_good_text_gives_the_result_in_both_modes(on_error) -> None:
    assert guarded_parse("x = 1\n", on_error, lambda text: len(text)) == 6


# ---------------------------------------------------------------- the line endings

@pytest.mark.parametrize("text", ["x = 1\r\ny = 2\r\n", "x = 1\ry = 2\r", "x = 1\ny = 2\r\n"], ids=["crlf", "cr", "mixed"])
def test_a_carriage_return_is_refused_without_asking_the_parser(text) -> None:
    calls: list[str] = []

    def parser(value: str) -> str:
        calls.append(value)
        return value

    with pytest.raises(ParamError) as info:
        guarded_parse(text, "raise", parser)
    assert calls == []
    assert "line endings" in info.value.problem


@pytest.mark.parametrize("text", ["x = 1\r\n", "x = 1\r"])
def test_a_carriage_return_with_keep_gives_none(text) -> None:
    assert guarded_parse(text, "keep", lambda value: value) is None


# ---------------------------------------------------------------- what the parser refuses

def test_a_syntax_error_becomes_a_card_that_names_the_line() -> None:
    with pytest.raises(ParamError) as info:
        guarded_parse("x = 1\ny = (\n", "raise", ast.parse)
    assert "line" in info.value.problem


def test_a_syntax_error_with_keep_gives_none() -> None:
    assert guarded_parse("x = (\n", "keep", ast.parse) is None


def _raising(error: BaseException):
    def parser(text: str):
        raise error
    return parser


@pytest.mark.parametrize(
    "error",
    [
        SyntaxError("bad", ("<s>", 1, 1, "x")),
        ValueError("boom"),
        RecursionError(),
        tokenize.TokenError("EOF in multi-line statement", (3, 0)),
    ],
    ids=["syntax-error", "value-error", "recursion-error", "token-error"],
)
def test_every_kind_of_refusal_is_a_card_or_none(error) -> None:
    with pytest.raises(ParamError):
        guarded_parse("x", "raise", _raising(error))
    assert guarded_parse("x", "keep", _raising(error)) is None


def test_the_reason_of_the_parser_is_in_the_card() -> None:
    with pytest.raises(ParamError) as info:
        guarded_parse("x", "raise", _raising(ValueError("the very reason")))
    assert "the very reason" in info.value.problem


def test_the_line_of_a_token_error_is_in_the_card() -> None:
    error = tokenize.TokenError("EOF in multi-line statement", (3, 0))
    with pytest.raises(ParamError) as info:
        guarded_parse("a\nb\nc\n", "raise", _raising(error))
    assert "line 3" in info.value.problem


@pytest.mark.parametrize("error", [KeyError("k"), TypeError("t"), ZeroDivisionError()])
def test_an_error_that_is_not_about_the_source_is_not_hidden(error) -> None:
    """A bug in the parser is not a bad file."""
    with pytest.raises(type(error)):
        guarded_parse("x", "keep", _raising(error))


def test_a_parser_may_return_a_falsy_result_and_it_is_returned() -> None:
    assert guarded_parse("", "raise", lambda text: []) == []
    assert guarded_parse("", "raise", lambda text: 0) == 0
