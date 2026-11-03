import ast
import pytest
from simplibs.extractor_python.logic._helpers import first_doc_line


def _node(source: str):
    return ast.parse(source).body[0]


def test_a_node_without_a_docstring_gives_nothing() -> None:
    assert first_doc_line(_node("def f(): ...\n")) == ""
    assert first_doc_line(_node("class A: ...\n")) == ""


def test_the_first_line_becomes_a_comment() -> None:
    assert first_doc_line(_node('def f():\n    """Do it."""\n')) == "  # Do it."


def test_a_class_and_an_async_function_have_one_too() -> None:
    assert first_doc_line(_node('class A:\n    """The class."""\n')) == "  # The class."
    assert first_doc_line(_node('async def f():\n    """The coroutine."""\n')) == "  # The coroutine."


def test_only_the_first_line_of_several_is_taken() -> None:
    source = 'def f():\n    """First.\n\n    Second.\n    Third.\n    """\n'
    assert first_doc_line(_node(source)) == "  # First."


def test_a_docstring_that_starts_on_the_next_line() -> None:
    source = 'def f():\n    """\n    First.\n    Second.\n    """\n'
    assert first_doc_line(_node(source)) == "  # First."


def test_the_blanks_around_the_line_are_dropped() -> None:
    assert first_doc_line(_node('def f():\n    """   Padded.   """\n')) == "  # Padded."


@pytest.mark.parametrize("docstring", ["", "   ", "\n\n"], ids=["empty", "blanks", "line-breaks"])
def test_an_empty_docstring_gives_nothing(docstring) -> None:
    assert first_doc_line(_node(f"def f():\n    {docstring!r}\n")) == ""


@pytest.mark.parametrize(
    "separator",
    ["\u2028", "\u2029", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\r"],
    ids=["u2028", "u2029", "vt", "ff", "fs", "gs", "rs", "nel", "cr"],
)
def test_every_kind_of_line_end_stops_the_comment(separator) -> None:
    """A comment that kept such a character would run on into the next line of the output."""
    source = f"def f():\n    {('Alpha' + separator + 'Beta')!r}\n"
    assert first_doc_line(_node(source)) == "  # Alpha"


def test_the_result_never_holds_a_line_break() -> None:
    result = first_doc_line(_node('def f():\n    """One\n    two"""\n'))
    assert "\n" not in result and "\r" not in result


def test_the_result_is_valid_after_a_signature() -> None:
    line = "def f(): ..." + first_doc_line(_node('def f():\n    """Doc."""\n'))
    ast.parse(line)
