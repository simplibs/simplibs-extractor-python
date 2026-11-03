import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.actions import RemovePythonComments, RemovePythonImports
from simplibs.extractor_python.logic import remove_python_comments, remove_python_imports

SAMPLES = [
    "x = 1  # note\n",
    "# only\nx = 1\n",
    "def f():\n    # c\n    return 1\n",
    'x = "a # b"  # real\n',
    "x = [\n    1,  # one\n    2,\n]\n",
    "",
]


def test_the_action_contract(subtests) -> None:
    assert_action(
        subtests,
        RemovePythonComments(),
        valid_values=["x = 1  # note\n", "# only\nx = 1\n", 'x = "a # b"\n', ""],
        expected_outputs=["x = 1\n", "x = 1\n", 'x = "a # b"\n', ""],
        invalid_values=[5, None, "x = (\n# c\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=str,
        expected_output_type=str,
        verbose=False,
    )


def test_is_an_action() -> None:
    assert isinstance(RemovePythonComments(), Action)


def test_the_class_has_the_agreed_name() -> None:
    assert type(RemovePythonComments()).__name__ == "RemovePythonComments"


@pytest.mark.parametrize("text", SAMPLES)
def test_does_what_the_function_does(text) -> None:
    assert RemovePythonComments()(text) == remove_python_comments(text)


def test_a_text_that_cannot_be_read_is_a_card_by_default() -> None:
    with pytest.raises(ParamError):
        RemovePythonComments()("x = (\n")


def test_on_error_keep_gives_the_text_back() -> None:
    assert RemovePythonComments(on_error="keep")("x = (\n# c\n") == "x = (\n# c\n"


@pytest.mark.parametrize("options", [{"on_error": "ignore"}, {"on_error": 5}, {"on_error": None}])
def test_a_wrong_option_is_refused(options) -> None:
    with pytest.raises(ValidationError):
        RemovePythonComments(**options)("x = 1\n")


def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(TypeError):
        RemovePythonComments(colour="red")  # type: ignore[call-arg]


def test_two_actions_chain_with_the_right_shift() -> None:
    chained = RemovePythonComments() >> RemovePythonImports()
    assert isinstance(chained, Action)
    text = "import os  # the os\nx = 1  # one\n"
    assert chained(text) == remove_python_imports(remove_python_comments(text))
    assert chained(text) == "x = 1\n"
