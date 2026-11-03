import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.actions import RemovePythonDecorators
from simplibs.extractor_python.logic import remove_python_decorators

SAMPLES = [
    "@dec\ndef f(): ...\n",
    "@a\n@b(1)\nclass A: ...\n",
    "class A:\n    @property\n    def p(self): ...\n",
    "x = a @ b\n",
    "",
]


def test_the_action_contract(subtests) -> None:
    assert_action(
        subtests,
        RemovePythonDecorators(),
        valid_values=["@dec\ndef f(): ...\n", "class A:\n    @property\n    def p(self): ...\n", "x = a @ b\n", ""],
        expected_outputs=["def f(): ...\n", "class A:\n    def p(self): ...\n", "x = a @ b\n", ""],
        invalid_values=[5, None, "@dec\ndef f(:\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=str,
        expected_output_type=str,
        verbose=False,
    )


def test_is_an_action() -> None:
    assert isinstance(RemovePythonDecorators(), Action)


def test_the_class_has_the_agreed_name() -> None:
    assert type(RemovePythonDecorators()).__name__ == "RemovePythonDecorators"


@pytest.mark.parametrize("text", SAMPLES)
def test_does_what_the_function_does(text) -> None:
    assert RemovePythonDecorators()(text) == remove_python_decorators(text)


def test_a_text_that_cannot_be_read_is_a_card_by_default() -> None:
    with pytest.raises(ParamError):
        RemovePythonDecorators()("def f(:\n")


def test_on_error_keep_gives_the_text_back() -> None:
    assert RemovePythonDecorators(on_error="keep")("@dec\ndef f(:\n") == "@dec\ndef f(:\n"


@pytest.mark.parametrize("options", [{"on_error": "ignore"}, {"on_error": 5}, {"on_error": None}])
def test_a_wrong_option_is_refused(options) -> None:
    with pytest.raises(ValidationError):
        RemovePythonDecorators(**options)("x = 1\n")


def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(TypeError):
        RemovePythonDecorators(colour="red")  # type: ignore[call-arg]
