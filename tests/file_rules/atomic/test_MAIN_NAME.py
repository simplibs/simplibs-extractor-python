from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import MAIN_NAME

VALID = ["__main__.py", "pkg/__main__.py", "a/b/c/__main__.py"]
INVALID = ["main.py", "__init__.py", "__main__.pyi", "pkg/__main__", "my__main__.py", "pkg/__main__.py/a.py", "a.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        MAIN_NAME,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", VALID)
def test_the_file_called_main_is_taken(path) -> None:
    assert MAIN_NAME(Path(path)) is True


@pytest.mark.parametrize("path", INVALID)
def test_any_other_name_is_not(path) -> None:
    assert MAIN_NAME(Path(path)) is False
