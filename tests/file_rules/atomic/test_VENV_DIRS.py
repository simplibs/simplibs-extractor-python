from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.constants import PYTHON_VENV_DIR_NAMES
from simplibs.extractor_python.file_rules import VENV_DIRS

VALID = ["venv/a.py", ".venv/lib/a.py", "env/a.py", "virtualenv/a.py", "pkg/.venv/x.py", "a/b/venv/c/d.py"]
INVALID = ["a.py", "pkg/a.py", "environment/a.py", "myvenv/a.py", "venv2/a.py", "venv.py", "pkg/env.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        VENV_DIRS,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("name", PYTHON_VENV_DIR_NAMES)
def test_every_name_of_the_constant_is_an_environment(name) -> None:
    assert VENV_DIRS(Path(name) / "a.py") is True
    assert VENV_DIRS(Path("pkg") / name / "deep" / "a.py") is True


@pytest.mark.parametrize("path", INVALID)
def test_a_folder_name_is_compared_as_a_whole(path) -> None:
    assert VENV_DIRS(Path(path)) is False
