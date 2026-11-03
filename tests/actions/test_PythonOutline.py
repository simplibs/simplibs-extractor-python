import ast
import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.extractor_python.actions import PythonOutline
from simplibs.extractor_python.logic import python_outline

SAMPLES = [
    "def f(a, b=1):\n    return a\n",
    '@dec\nclass A(B):\n    """The class."""\n    def m(self, a: int = 1) -> str:\n        """Do it."""\n        return ""\n',
    "x = 1\nimport os\n",
    "",
]


def test_the_action_contract(subtests) -> None:
    assert_action(
        subtests,
        PythonOutline(),
        valid_values=["def f(a):\n    return a\n", "class A:\n    x = 1\n", "x = 1\n"],
        expected_outputs=["def f(a): ...\n", "class A: ...\n", ""],
        invalid_values=[5, None, "def f(:\n"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=str,
        expected_output_type=str,
        verbose=False,
    )


def test_is_an_action() -> None:
    assert isinstance(PythonOutline(), Action)


def test_the_class_has_the_agreed_name() -> None:
    assert type(PythonOutline()).__name__ == "PythonOutline"


@pytest.mark.parametrize("text", SAMPLES)
@pytest.mark.parametrize("docstrings", [True, False])
def test_does_what_the_function_does(text, docstrings) -> None:
    assert PythonOutline(docstrings=docstrings)(text) == python_outline(text, docstrings=docstrings)


def test_the_docstrings_are_on_by_default() -> None:
    text = 'def f():\n    """Do it."""\n'
    assert PythonOutline()(text) == "def f(): ...  # Do it.\n"
    assert PythonOutline(docstrings=False)(text) == "def f(): ...\n"


def test_a_text_that_does_not_parse_is_a_card_by_default() -> None:
    with pytest.raises(ParamError):
        PythonOutline()("def f(:\n")


def test_on_error_keep_gives_the_whole_text_back() -> None:
    assert PythonOutline(on_error="keep")("def f(:\n") == "def f(:\n"


@pytest.mark.parametrize("options", [{"on_error": "ignore"}, {"on_error": 5}, {"docstrings": "yes"}, {"docstrings": None}])
def test_a_wrong_option_is_refused(options) -> None:
    """Whether the card comes on construction or on the first call is the business of `create_action`."""
    with pytest.raises(ValidationError):
        PythonOutline(**options)("def f(): ...\n")


def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(TypeError):
        PythonOutline(colour="red")  # type: ignore[call-arg]


def test_the_result_can_be_chained_further() -> None:
    chained = PythonOutline(docstrings=False) >> PythonOutline(docstrings=False)
    assert isinstance(chained, Action)
    assert chained("def f(a):\n    return a\n") == "def f(a): ...\n"


def test_the_output_is_valid_python() -> None:
    for text in SAMPLES:
        ast.parse(PythonOutline()(text))
