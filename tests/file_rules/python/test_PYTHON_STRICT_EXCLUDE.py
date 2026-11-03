from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import PYTHON_STRICT_EXCLUDE

TESTS = ["test_a.py", "tests/a.py", "pkg/conftest.py"]
CONFIG = ["setup.py", "pkg/tox.ini", "requirements.txt"]
ENVIRONMENTS = ["venv/lib/a.py", ".venv/a.py", "env/a.py"]
OUTPUT = ["build/lib/a.py", "dist/a.py", "pkg/out/a.py"]
VCS = [".git/hooks/a.py", ".svn/a.py"]
PROJECT_CODE = ["a.py", "pkg/a.py", "pkg/__init__.py", "pkg/__main__.py", "latest_data.py", "contest.py", "pkg/env.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        PYTHON_STRICT_EXCLUDE,
        valid_values=[Path(path) for path in [*TESTS, *CONFIG, *ENVIRONMENTS, *OUTPUT, *VCS]],
        invalid_values=[Path(path) for path in PROJECT_CODE],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", TESTS)
def test_tests_are_excluded(path) -> None:
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is True


@pytest.mark.parametrize("path", CONFIG)
def test_configuration_is_excluded(path) -> None:
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is True


@pytest.mark.parametrize("path", ENVIRONMENTS)
def test_environments_are_excluded(path) -> None:
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is True


@pytest.mark.parametrize("path", OUTPUT)
def test_build_output_is_excluded(path) -> None:
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is True


@pytest.mark.parametrize("path", VCS)
def test_version_control_is_excluded(path) -> None:
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is True


@pytest.mark.parametrize("path", PROJECT_CODE)
def test_the_code_of_the_project_is_not(path) -> None:
    """Only what the project does stays; `__init__.py` and `__main__.py` are part of it."""
    assert PYTHON_STRICT_EXCLUDE(Path(path)) is False
