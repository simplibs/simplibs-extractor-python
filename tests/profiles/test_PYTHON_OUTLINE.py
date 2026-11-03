import ast
import pytest
from simplibs.exception import ParamError
from simplibs.extractor import Profile
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.profiles import PYTHON_OUTLINE


def test_is_a_profile() -> None:
    assert isinstance(PYTHON_OUTLINE, Profile)


def test_profile_contract(subtests) -> None:
    assert_profile(
        subtests,
        PYTHON_OUTLINE,
        expected_key="python/outline",
        expected_output_name="python_outline.md",
        expected_format="markdown",
        included=("a.py", "pkg/a.py", "pkg/__init__.py", "pkg/__main__.py", "tests/test_a.py"),
        excluded=("README.md", "pkg/a.pyi", ".hidden.py", "__pycache__/a.py", "pkg/a.txt"),
        step_cases={
            ".py": [
                ("def f(a):\n    return a\n", "def f(a): ...\n"),
                ("class A:\n    x = 1\n", "class A: ...\n"),
                ('def f():\n    """Do it."""\n', "def f(): ...  # Do it.\n"),
                ("x = 1\n", ""),
            ]
        },
        unchanged_suffixes=(".md", ".txt", ".js"),
        cover_all_suffixes=True,
        verbose=False,
    )


def test_only_the_python_suffix_has_steps() -> None:
    assert set(PYTHON_OUTLINE.steps) == {".py"}


def test_the_first_line_of_each_docstring_is_kept_as_a_comment() -> None:
    result = PYTHON_OUTLINE.steps[".py"]('class A:\n    """The class."""\n    def m(self):\n        """Do it."""\n')
    assert result == "class A:  # The class.\n    def m(self): ...  # Do it.\n"


def test_each_file_is_valid_python_again() -> None:
    ast.parse(PYTHON_OUTLINE.steps[".py"]('@dec\nclass A(B):\n    def m(self, a: int = 1) -> str:\n        return ""\n'))


def test_a_file_that_is_not_python_makes_its_step_raise() -> None:
    with pytest.raises(ParamError):
        PYTHON_OUTLINE.steps[".py"]("def f(:\n")
