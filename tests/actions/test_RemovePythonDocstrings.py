import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.actions import RemovePythonComments, RemovePythonDocstrings
from simplibs.extractor_python.logic import remove_python_comments, remove_python_docstrings

SAMPLES = [
    '"""Module."""\nx = 1\n',
    'def f():\n    """Doc."""\n    return 1\n',
    'class A:\n    """Only a docstring."""\n',
    "def f():\n    'one'\n    'two'\n",
    "",
]


def test_the_action_contract(subtests) -> None:
    assert_action(
        subtests,
        RemovePythonDocstrings(),
        valid_values=['"""Module."""\nx = 1\n', 'def f():\n    """Doc."""\n    return 1\n', 'def f():\n    """Only."""\n', ""],
        expected_outputs=["x = 1\n", "def f():\n    return 1\n", "def f():\n    pass\n", ""],
        invalid_values=[5, None, 'def f(:\n    """Doc."""\n'],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=str,
        expected_output_type=str,
        verbose=False,
    )


def test_is_an_action() -> None:
    assert isinstance(RemovePythonDocstrings(), Action)


def test_the_class_has_the_agreed_name() -> None:
    assert type(RemovePythonDocstrings()).__name__ == "RemovePythonDocstrings"


@pytest.mark.parametrize("text", SAMPLES)
def test_does_what_the_function_does(text) -> None:
    assert RemovePythonDocstrings()(text) == remove_python_docstrings(text)


def test_a_text_that_cannot_be_read_is_a_card_by_default() -> None:
    with pytest.raises(ParamError):
        RemovePythonDocstrings()("def f(:\n")


def test_on_error_keep_gives_the_text_back() -> None:
    assert RemovePythonDocstrings(on_error="keep")("def f(:\n") == "def f(:\n"


@pytest.mark.parametrize("options", [{"on_error": "ignore"}, {"on_error": 5}, {"on_error": None}])
def test_a_wrong_option_is_refused(options) -> None:
    with pytest.raises(ValidationError):
        RemovePythonDocstrings(**options)("x = 1\n")


def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(TypeError):
        RemovePythonDocstrings(colour="red")  # type: ignore[call-arg]


def test_comments_then_docstrings_in_one_pipeline() -> None:
    chained = RemovePythonComments() >> RemovePythonDocstrings()
    assert isinstance(chained, Action)
    text = 'def f():\n    """Doc."""\n    # note\n    return 1\n'
    assert chained(text) == remove_python_docstrings(remove_python_comments(text))
    assert chained(text) == "def f():\n    return 1\n"
