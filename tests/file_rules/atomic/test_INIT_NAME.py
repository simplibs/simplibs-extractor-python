from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import INIT_NAME

VALID = ["__init__.py", "pkg/__init__.py", "a/b/c/__init__.py"]
INVALID = ["init.py", "__main__.py", "__init__.pyi", "pkg/__init__", "my__init__.py", "pkg/__init__.py/a.py", "a.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        INIT_NAME,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", VALID)
def test_the_file_called_init_is_taken(path) -> None:
    assert INIT_NAME(Path(path)) is True


@pytest.mark.parametrize("path", INVALID)
def test_any_other_name_is_not(path) -> None:
    assert INIT_NAME(Path(path)) is False
