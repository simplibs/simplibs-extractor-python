import pytest
from simplibs.exception import ParamError
from simplibs.extractor import Profile
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.presets import PYTHON_NO_IMPORTS
from simplibs.extractor_python.profiles import PYTHON_CODE_NO_IMPORTS


def test_is_a_profile() -> None:
    assert isinstance(PYTHON_CODE_NO_IMPORTS, Profile)


def test_profile_contract(subtests) -> None:
    assert_profile(
        subtests,
        PYTHON_CODE_NO_IMPORTS,
        expected_key="python/code-no-imports",
        expected_output_name="python_code_no_imports.md",
        expected_format="markdown",
        included=("a.py", "pkg/a.py", "pkg/__init__.py", "pkg/__main__.py", "tests/test_a.py", "setup.py"),
        excluded=("README.md", "pkg/a.pyi", ".hidden.py", "__pycache__/a.py", "pkg/a.txt"),
        unchanged_suffixes=(".md", ".txt", ".pyi", ".js"),
        verbose=False,
    )


def test_nothing_is_excluded_by_a_second_rule() -> None:
    assert PYTHON_CODE_NO_IMPORTS.exclude is None


def test_only_the_python_suffix_has_steps() -> None:
    assert set(PYTHON_CODE_NO_IMPORTS.steps) == {".py"}


def test_the_python_suffix_uses_the_no_imports_preset() -> None:
    assert PYTHON_CODE_NO_IMPORTS.steps[".py"] is PYTHON_NO_IMPORTS


def test_a_file_is_reduced_to_its_logic() -> None:
    result = PYTHON_CODE_NO_IMPORTS.steps[".py"]("import os\n\n@dec\ndef f(a):\n    return a  # c\n")
    assert result.strip("\n") == "def f(a):\n    return a"


def test_a_file_that_is_not_python_makes_its_step_raise() -> None:
    with pytest.raises(ParamError):
        PYTHON_CODE_NO_IMPORTS.steps[".py"]("def f(:\n")
