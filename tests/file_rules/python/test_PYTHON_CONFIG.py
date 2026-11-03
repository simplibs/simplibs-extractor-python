from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.constants import PYTHON_CONFIG_NAMES
from simplibs.extractor_python.file_rules import PYTHON_CONFIG

VALID = ["setup.py", "pkg/setup.cfg", "pyproject.toml", "Pipfile", "a/b/requirements.txt", "tox.ini", "pytest.ini"]
INVALID = [
    "a.py",
    "pkg/config.py",
    "setup2.py",
    "my_setup.py",
    "pyproject.toml.bak",
    "requirements-dev.txt",
    "pipfile",
    "setup.py/a.py",
]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        PYTHON_CONFIG,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("name", PYTHON_CONFIG_NAMES)
def test_every_name_of_the_constant_is_configuration(name) -> None:
    assert PYTHON_CONFIG(Path(name)) is True
    assert PYTHON_CONFIG(Path("pkg") / name) is True


@pytest.mark.parametrize("path", INVALID)
def test_only_a_whole_name_counts(path) -> None:
    assert PYTHON_CONFIG(Path(path)) is False
