from simplibs.extractor import Profile
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.profiles import PYTHON_DATA_ALL


def test_is_a_profile() -> None:
    assert isinstance(PYTHON_DATA_ALL, Profile)


def test_profile_contract(subtests) -> None:
    assert_profile(
        subtests,
        PYTHON_DATA_ALL,
        expected_key="python/data-all",
        expected_output_name="python_data_all.md",
        expected_format="markdown",
        included=("a.py", "pkg/a.py", "pkg/__init__.py", "pkg/__main__.py", "tests/test_a.py", "setup.py"),
        excluded=("README.md", "pkg/a.pyi", ".hidden.py", "__pycache__/a.py", "pkg/a.txt"),
        step_cases={".py": [("x = 1  # c\n", "x = 1  # c\n"), ("def f(:\n", "def f(:\n")]},
        unchanged_suffixes=(".md", ".txt", ".js"),
        verbose=False,
    )


def test_there_are_no_steps_at_all() -> None:
    assert PYTHON_DATA_ALL.steps is None


def test_nothing_is_excluded_by_a_second_rule() -> None:
    assert PYTHON_DATA_ALL.exclude is None


def test_a_file_that_is_not_python_cannot_fail_here() -> None:
    """No step reads the text, so a broken file is output as it is."""
    from simplibs.extractor.logic import apply_steps

    assert apply_steps("def f(:\r\n", PYTHON_DATA_ALL.steps, ".py") == "def f(:\r\n"
