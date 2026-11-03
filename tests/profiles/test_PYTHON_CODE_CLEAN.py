import pytest
from simplibs.exception import ParamError
from simplibs.extractor import Profile
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.presets import PYTHON_CLEAN
from simplibs.extractor_python.profiles import PYTHON_CODE_CLEAN


def test_is_a_profile() -> None:
    assert isinstance(PYTHON_CODE_CLEAN, Profile)


def test_profile_contract(subtests) -> None:
    assert_profile(
        subtests,
        PYTHON_CODE_CLEAN,
        expected_key="python/code-clean",
        expected_output_name="python_code_clean.md",
        expected_format="markdown",
        included=(
            "a.py",
            "pkg/a.py",
            "pkg/__init__.py",
            "pkg/__main__.py",
            "latest_data.py",
            "tests/test_a.py",
            "setup.py",
        ),
        excluded=(
            "README.md",
            "pkg/a.txt",
            "pkg/a.pyi",
            ".hidden.py",
            "pkg/.hidden.py",
            "__pycache__/a.py",
            "pkg/__pycache__/__init__.py",
        ),
        unchanged_suffixes=(".md", ".txt", ".pyi", ".js"),
        verbose=False,
    )


def test_tests_and_configuration_are_included_here_unlike_in_src_clean() -> None:
    assert PYTHON_CODE_CLEAN.exclude is None


def test_only_the_python_suffix_has_steps() -> None:
    assert set(PYTHON_CODE_CLEAN.steps) == {".py"}


def test_the_python_suffix_uses_the_clean_preset() -> None:
    assert PYTHON_CODE_CLEAN.steps[".py"] is PYTHON_CLEAN


def test_a_file_is_cleaned() -> None:
    result = PYTHON_CODE_CLEAN.steps[".py"]('import os\n"""Doc."""\nx = os.name  # c\n')
    assert "#" not in result
    assert "import os" in result
    assert "x = os.name" in result


def test_a_file_that_is_not_python_makes_its_step_raise() -> None:
    """The extractor turns it into an `error` of that one file; the others go on."""
    with pytest.raises(ParamError):
        PYTHON_CODE_CLEAN.steps[".py"]("def f(:\n")
