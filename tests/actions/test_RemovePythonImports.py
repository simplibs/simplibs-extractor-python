import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.actions import RemovePythonImports
from simplibs.extractor_python.logic import remove_python_imports

SAMPLES = [
    "import os\nx = 1\n",
    "def f():\n    import os\n",
    "try:\n    import a\nexcept ImportError:\n    import b\n",
    "import a; x = 1\n",
    "",
]


def test_the_action_contract(subtests) -> None:
    assert_action(
        subtests,
        RemovePythonImports(),
        valid_values=["import os\nx = 1\n", "def f():\n    import os\n", "x = 1; import a\n", ""],
        expected_outputs=["x = 1\n", "def f():\n    pass\n", "x = 1\n", ""],
        invalid_values=[5, None, "import os\nx = (\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=str,
        expected_output_type=str,
        verbose=False,
    )


def test_is_an_action() -> None:
    assert isinstance(RemovePythonImports(), Action)


def test_the_class_has_the_agreed_name() -> None:
    assert type(RemovePythonImports()).__name__ == "RemovePythonImports"


@pytest.mark.parametrize("text", SAMPLES)
def test_does_what_the_function_does(text) -> None:
    assert RemovePythonImports()(text) == remove_python_imports(text)


def test_a_text_that_cannot_be_read_is_a_card_by_default() -> None:
    with pytest.raises(ParamError):
        RemovePythonImports()("x = (\n")


def test_on_error_keep_gives_the_text_back() -> None:
    assert RemovePythonImports(on_error="keep")("import os\nx = (\n") == "import os\nx = (\n"


@pytest.mark.parametrize("options", [{"on_error": "ignore"}, {"on_error": 5}, {"on_error": None}])
def test_a_wrong_option_is_refused(options) -> None:
    with pytest.raises(ValidationError):
        RemovePythonImports(**options)("x = 1\n")


def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(TypeError):
        RemovePythonImports(colour="red")  # type: ignore[call-arg]
