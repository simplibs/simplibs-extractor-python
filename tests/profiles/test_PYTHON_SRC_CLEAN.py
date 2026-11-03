import pytest
from simplibs.exception import ParamError
from simplibs.extractor import Profile
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.file_rules import PYTHON_STRICT_EXCLUDE
from simplibs.extractor_python.presets import PYTHON_CLEAN
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN


def test_is_a_profile() -> None:
    assert isinstance(PYTHON_SRC_CLEAN, Profile)


def test_profile_contract(subtests) -> None:
    assert_profile(
        subtests,
        PYTHON_SRC_CLEAN,
        expected_key="python/src-clean",
        expected_output_name="python_src_clean.md",
        expected_format="markdown",
        included=("a.py", "pkg/a.py", "pkg/__init__.py", "pkg/__main__.py", "latest_data.py", "contest.py"),
        excluded=(
            "tests/test_a.py",
            "test_a.py",
            "pkg/a_test.py",
            "conftest.py",
            "setup.py",
            "tox.ini",
            "venv/lib/a.py",
            ".venv/a.py",
            "build/lib/a.py",
            "dist/a.py",
            ".git/hooks/a.py",
            "README.md",
            "pkg/a.pyi",
            ".hidden.py",
            "__pycache__/a.py",
        ),
        unchanged_suffixes=(".md", ".txt", ".pyi", ".js"),
        verbose=False,
    )


def test_it_uses_the_strict_exclusion() -> None:
    assert PYTHON_SRC_CLEAN.exclude is PYTHON_STRICT_EXCLUDE


def test_only_the_python_suffix_has_steps() -> None:
    assert set(PYTHON_SRC_CLEAN.steps) == {".py"}


def test_the_python_suffix_uses_the_clean_preset() -> None:
    assert PYTHON_SRC_CLEAN.steps[".py"] is PYTHON_CLEAN


def test_a_file_is_cleaned() -> None:
    result = PYTHON_SRC_CLEAN.steps[".py"]('"""Doc."""\nimport os\nx = os.name  # c\n')
    assert "#" not in result
    assert "Doc" not in result
    assert "import os" in result


def test_a_file_that_is_not_python_makes_its_step_raise() -> None:
    with pytest.raises(ParamError):
        PYTHON_SRC_CLEAN.steps[".py"]("def f(:\n")
