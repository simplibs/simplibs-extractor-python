import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor_python.logic._validations import raise_python_source_error

TEXT = "x = 1\ny = (\nz = 3\n"


def test_the_card(subtests) -> None:
    assert_exception_function(
        subtests,
        raise_python_source_error,
        invalid_params=(TEXT, "'(' was never closed", 2),
        exception_type=ParamError,
        error_name="CODE_EXTRACTOR_PYTHON_SOURCE_INVALID",
        label="text",
        value="y = (",
        exception=ValueError,
        verbose=False,
    )


def _card(*args) -> ParamError:
    with pytest.raises(ParamError) as info:
        raise_python_source_error(*args)
    return info.value


def test_it_always_raises() -> None:
    for args in [(TEXT, "bad"), (TEXT, "bad", 1), ("", "bad"), (TEXT, "bad", None)]:
        with pytest.raises(ParamError):
            raise_python_source_error(*args)


def test_the_problem_names_the_reason_and_the_line() -> None:
    problem = _card(TEXT, "'(' was never closed", 2).problem
    assert "'(' was never closed" in problem
    assert "(line 2)" in problem


def test_the_value_is_the_line_of_the_problem_without_its_blanks() -> None:
    assert _card("a\n    indented = (   \nc\n", "bad", 2).value == "indented = ("


def test_the_first_and_the_last_line_can_be_shown() -> None:
    assert _card(TEXT, "bad", 1).value == "x = 1"
    assert _card("a\nb", "bad", 2).value == "b"


def test_without_a_line_the_start_of_the_text_is_shown_and_no_line_is_named() -> None:
    card = _card(TEXT, "bad")
    assert card.value == TEXT[:80]
    assert "(line" not in card.problem


def test_a_long_text_is_shown_only_by_its_first_eighty_characters() -> None:
    assert _card("x" * 500, "bad").value == "x" * 80


@pytest.mark.parametrize("line", [0, -1, 99])
def test_a_line_that_is_not_in_the_text_is_treated_as_no_line(line) -> None:
    card = _card(TEXT, "bad", line)
    assert card.value == TEXT[:80]
    assert "(line" not in card.problem


def test_the_expectation_names_python_and_the_line_endings() -> None:
    expected = _card(TEXT, "bad", 1).expected
    assert "Python 3" in expected
    assert "\\n" in expected


def test_the_hints_say_how_to_fix_it_leave_it_out_normalize_or_keep() -> None:
    how_to_fix = _card(TEXT, "bad", 1).how_to_fix
    assert isinstance(how_to_fix, (tuple, list)) and len(how_to_fix) == 3
    joined = " ".join(how_to_fix)
    assert "exclude" in joined
    assert "\\r\\n" in joined
    assert "on_error='keep'" in joined


def test_an_empty_text_is_shown_as_empty() -> None:
    assert _card("", "bad").value == ""
