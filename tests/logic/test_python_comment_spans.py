import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.logic import python_comment_spans


def _found(text: str) -> list[str]:
    """The text of every span the function finds (the blanks in front of the comment included)."""
    return [text[start:end] for start, end in python_comment_spans(text)]


def test_a_text_without_comments_has_no_spans() -> None:
    assert python_comment_spans("x = 1\ndef f(): ...\n") == []
    assert python_comment_spans("") == []


def test_returns_a_list_of_pairs_of_ints() -> None:
    spans = python_comment_spans("x = 1  # a\n# b\n")
    assert isinstance(spans, list)
    for span in spans:
        assert isinstance(span, tuple) and len(span) == 2
        assert all(isinstance(offset, int) for offset in span)


def test_a_comment_after_code_is_taken_with_the_blanks_in_front_of_it() -> None:
    assert _found("x = 1  # note\n") == ["  # note"]


def test_a_comment_on_its_own_line_is_taken_with_its_indentation() -> None:
    assert _found("def f():\n    # c\n    return 1\n") == ["    # c"]


def test_a_tab_in_front_is_a_blank_too() -> None:
    assert _found("x = 1\t# c\n") == ["\t# c"]


def test_a_comment_at_the_end_of_a_text_without_a_final_newline() -> None:
    assert _found("x = 1  # c") == ["  # c"]


def test_the_comments_come_in_the_order_of_the_text() -> None:
    assert _found("# a\nx = 1  # b\n# c\n") == ["# a", "  # b", "# c"]


def test_a_comment_inside_a_bracket() -> None:
    assert _found("x = [\n    1,  # one\n    2,\n]\n") == ["  # one"]


@pytest.mark.parametrize(
    "text",
    ['x = "a # b"\n', "x = 'a # b'\n", "x = '''# not\n# a comment'''\n", 'x = """\n# no\n"""\n', "x = r'#'\n", "x = b'#'\n"],
    ids=["double", "single", "triple-single", "triple-double", "raw", "bytes"],
)
def test_a_hash_inside_a_string_is_not_a_comment(text) -> None:
    assert python_comment_spans(text) == []


def test_a_string_and_a_comment_on_one_line() -> None:
    assert _found('x = "a # b"  # real\n') == ["  # real"]


def test_the_shebang_and_the_coding_line_are_comments() -> None:
    assert _found("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nx = 1\n") == [
        "#!/usr/bin/env python",
        "# -*- coding: utf-8 -*-",
    ]


def test_wide_characters_before_the_comment() -> None:
    assert _found('x = "č€😀"  # c\ny = 2  # d\n') == ["  # c", "  # d"]


def test_wide_characters_in_the_comment() -> None:
    assert _found("x = 1  # čau 😀\n") == ["  # čau 😀"]


@pytest.mark.parametrize("text", ["x = = 1  # c\n", "print 'old'  # c\n", "def f(a b):  # c\n    pass\n"])
def test_it_needs_only_a_text_that_can_be_tokenized_not_valid_python(text) -> None:
    assert _found(text) == ["  # c"]


# ---------------------------------------------------------------- a text that cannot be tokenized

def test_an_unclosed_bracket_is_a_card() -> None:
    with pytest.raises(ParamError):
        python_comment_spans("x = (\n# c\n")


def test_an_unclosed_bracket_with_keep_gives_no_spans() -> None:
    assert python_comment_spans("x = (\n# c\n", on_error="keep") == []


@pytest.mark.parametrize("text", ["x = 1  # c\r\n", "x = 1  # c\r"])
def test_other_line_endings_are_a_card(text) -> None:
    with pytest.raises(ParamError):
        python_comment_spans(text)
    assert python_comment_spans(text, on_error="keep") == []


def test_the_default_of_on_error_is_raise() -> None:
    with pytest.raises(ParamError):
        python_comment_spans("x = (\n")


# ---------------------------------------------------------------- the arguments

@pytest.mark.parametrize("value", [None, 5, b"x = 1", ["x = 1"]])
def test_the_text_must_be_a_str(value) -> None:
    with pytest.raises(ValidationError):
        python_comment_spans(value)


@pytest.mark.parametrize("value", ["ignore", "RAISE", "", None, True])
def test_on_error_accepts_only_the_two_agreed_words(value) -> None:
    with pytest.raises(ValidationError):
        python_comment_spans("x = 1\n", on_error=value)


def test_on_error_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        python_comment_spans("x = 1\n", "keep")  # type: ignore[misc]
