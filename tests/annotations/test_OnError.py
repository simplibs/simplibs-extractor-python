import typing
from simplibs.extractor_python.annotations import OnError


def test_is_a_literal() -> None:
    assert typing.get_origin(OnError) is typing.Literal


def test_the_two_agreed_words() -> None:
    """`raise` makes a card of a source that cannot be read; `keep` returns the text unchanged."""
    assert typing.get_args(OnError) == ("raise", "keep")
