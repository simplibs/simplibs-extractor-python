from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import IN_DUNDER_DIR

VALID = [
    "__pycache__/a.py",
    "pkg/__pycache__/a.cpython-312.pyc",
    "__pypackages__/x/a.py",
    "a/__b__/c.py",
    "a/__cache/b/c.py",
]
INVALID = ["a.py", "pkg/a.py", "__init__.py", "pkg/__init__.py", "pkg/__main__.py", "_private/a.py", "pkg/_x_/a.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        IN_DUNDER_DIR,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", VALID)
def test_a_folder_that_starts_with_two_underscores_above_the_file_counts(path) -> None:
    assert IN_DUNDER_DIR(Path(path)) is True


@pytest.mark.parametrize("path", INVALID)
def test_other_paths_do_not(path) -> None:
    assert IN_DUNDER_DIR(Path(path)) is False


@pytest.mark.parametrize("path", ["__init__.py", "pkg/__init__.py", "pkg/__main__.py"])
def test_a_dunder_file_is_not_a_dunder_folder(path) -> None:
    """`__init__.py` and `__main__.py` stay readable; only FOLDERS made by the interpreter are left out."""
    assert IN_DUNDER_DIR(Path(path)) is False
