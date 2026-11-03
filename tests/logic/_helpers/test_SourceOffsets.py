import ast
import pytest
from simplibs.extractor_python.logic._helpers import SourceOffsets


def test_has_no_instance_dict() -> None:
    assert not hasattr(SourceOffsets("x"), "__dict__")


# ---------------------------------------------------------------- token positions (characters)

def test_a_token_position_is_the_start_of_the_line_plus_the_column() -> None:
    offsets = SourceOffsets("ab\ncd\n")
    assert offsets.token_offset(1, 0) == 0
    assert offsets.token_offset(1, 2) == 2
    assert offsets.token_offset(2, 0) == 3
    assert offsets.token_offset(2, 1) == 4


def test_the_empty_line_after_the_last_newline_has_a_start_too() -> None:
    assert SourceOffsets("ab\ncd\n").token_offset(3, 0) == 6


# ---------------------------------------------------------------- ast positions (bytes)

def test_ascii_text_has_one_byte_per_character() -> None:
    offsets = SourceOffsets("ab\ncd\n")
    assert offsets.ast_offset(1, 1) == 1
    assert offsets.ast_offset(2, 1) == 4


@pytest.mark.parametrize("character", ["č", "€", "😀", "ж"], ids=["2-bytes", "3-bytes", "4-bytes", "cyrillic"])
def test_a_node_after_a_wide_character_is_cut_at_the_right_place(character) -> None:
    """`ast` counts the column in UTF-8 bytes; the span must be in characters, because strings are cut by those."""
    text = f'x = "{character}"\ny = 1\n'
    tree = ast.parse(text)
    offsets = SourceOffsets(text)

    start, end = offsets.span_of(tree.body[0].value)
    assert text[start:end] == f'"{character}"'

    start, end = offsets.span_of(tree.body[1])
    assert text[start:end] == "y = 1"


@pytest.mark.parametrize("character", ["č", "€", "😀"])
def test_a_second_statement_on_the_same_line_as_a_wide_character(character) -> None:
    text = f'a = "{character}"; b = "{character}"\n'
    tree = ast.parse(text)
    offsets = SourceOffsets(text)
    start, end = offsets.span_of(tree.body[1])
    assert text[start:end] == f'b = "{character}"'


def test_column_zero_of_a_line_after_a_wide_character_is_its_start() -> None:
    text = 'x = "č"\ny = 1\n'
    assert SourceOffsets(text).ast_offset(2, 0) == text.index("y")


def test_the_last_line_may_have_no_newline() -> None:
    text = 'x = "č"'
    tree = ast.parse(text)
    assert SourceOffsets(text).span_of(tree.body[0]) == (0, 7)


# ---------------------------------------------------------------- span_of

def test_span_of_a_node_on_one_line() -> None:
    text = "x = 1\ny = 2\n"
    tree = ast.parse(text)
    assert SourceOffsets(text).span_of(tree.body[0]) == (0, 5)
    assert SourceOffsets(text).span_of(tree.body[1]) == (6, 11)


def test_span_of_a_node_over_several_lines() -> None:
    text = "def f():\n    pass\n"
    tree = ast.parse(text)
    start, end = SourceOffsets(text).span_of(tree.body[0])
    assert text[start:end] == "def f():\n    pass"


def test_span_of_an_indented_node() -> None:
    text = "def f():\n    import os\n"
    tree = ast.parse(text)
    start, end = SourceOffsets(text).span_of(tree.body[0].body[0])
    assert text[start:end] == "import os"
