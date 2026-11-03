import ast
import pytest
from simplibs.extractor_python.logic._helpers import SourceOffsets, find_decorator_spans


def _found(text: str) -> list[str]:
    """The text of every span the function finds."""
    spans = find_decorator_spans(text, ast.parse(text), SourceOffsets(text))
    return [text[start:end] for start, end in spans]


def test_a_text_without_decorators_has_no_spans() -> None:
    assert _found("def f(): ...\nclass A: ...\n") == []


def test_a_decorator_is_found_from_its_at_sign_to_its_end() -> None:
    assert _found("@dec\ndef f(): ...\n") == ["@dec"]


def test_the_span_does_not_take_the_line_break() -> None:
    text = "@dec\ndef f(): ...\n"
    (start, end), = find_decorator_spans(text, ast.parse(text), SourceOffsets(text))
    assert text[end] == "\n"


@pytest.mark.parametrize(
    "decorator",
    ["@a.b", "@a.b(1, 2)", "@a.b(x='@')", '@route("a@b")', "@dec(a @ b)", "@ dec", "@a[0]", "@(factory)", "@((dec))"],
    ids=["attribute", "call", "string-argument", "string-with-at", "matmul", "space", "subscript", "brackets", "double-brackets"],
)
def test_a_decorator_of_any_shape_is_found_whole(decorator) -> None:
    assert _found(f"{decorator}\ndef f(): ...\n") == [decorator]


def test_a_decorator_over_several_lines() -> None:
    assert _found("@dec(\n    1,\n    2,\n)\ndef f(): ...\n") == ["@dec(\n    1,\n    2,\n)"]


def test_every_decorator_of_one_definition() -> None:
    assert _found("@a\n@b(1)\n@c.d\ndef f(): ...\n") == ["@a", "@b(1)", "@c.d"]


def test_a_class_a_function_and_an_async_function() -> None:
    text = "@a\nclass A: ...\n@b\ndef f(): ...\n@c\nasync def g(): ...\n"
    assert _found(text) == ["@a", "@b", "@c"]


def test_decorators_of_methods_and_nested_definitions_are_found_too() -> None:
    text = "class A:\n    @property\n    def p(self): ...\n    @staticmethod\n    def s(): ...\n\ndef f():\n    @inner\n    def g(): ...\n"
    assert sorted(_found(text)) == ["@inner", "@property", "@staticmethod"]


def test_an_at_sign_in_an_earlier_string_is_not_taken_for_the_decorator() -> None:
    assert _found('x = "a@b"\n@dec\ndef f(): ...\n') == ["@dec"]


def test_wide_characters_before_the_decorator() -> None:
    assert _found('x = "č€😀"\n@dec\ndef f(): ...\n') == ["@dec"]


def test_a_decorator_after_a_comment_with_an_at_sign() -> None:
    assert _found("# mail me@home\n@dec\ndef f(): ...\n") == ["@dec"]


def test_spans_are_pairs_of_ints_in_the_text() -> None:
    text = "@a\ndef f(): ...\n"
    for start, end in find_decorator_spans(text, ast.parse(text), SourceOffsets(text)):
        assert isinstance(start, int) and isinstance(end, int)
        assert 0 <= start < end <= len(text)


def test_blanks_and_line_breaks_inside_the_brackets() -> None:
    assert _found("@(factory )\ndef f(): ...\n") == ["@(factory )"]
    assert _found("@(\n    factory\n)\ndef f(): ...\n") == ["@(\n    factory\n)"]


def test_a_comment_inside_the_brackets_stays_in_the_span() -> None:
    assert _found("@(dec  # note\n)\ndef f(): ...\n") == ["@(dec  # note\n)"]


def test_a_closing_bracket_in_a_comment_is_not_taken_for_the_real_one() -> None:
    assert _found("@(dec  # note)\n)\ndef f(): ...\n") == ["@(dec  # note)\n)"]


def test_an_opening_bracket_in_a_comment_is_not_counted() -> None:
    assert _found("@(  # (x\n    dec)\ndef f(): ...\n") == ["@(  # (x\n    dec)"]


def test_an_at_sign_in_a_comment_inside_the_brackets_is_not_taken_for_the_decorator() -> None:
    assert _found("@(  # mail me@home\n    dec)\ndef f(): ...\n") == ["@(  # mail me@home\n    dec)"]


def test_a_bracketed_decorator_with_windows_line_breaks() -> None:
    assert _found("@(  # (\r\n    dec  # )\r\n)\r\ndef f(): ...\r\n") == ["@(  # (\r\n    dec  # )\r\n)"]