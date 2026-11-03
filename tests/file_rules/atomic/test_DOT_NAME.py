from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import DOT_NAME

VALID = [".env", ".gitignore", "pkg/.hidden.py", "a/b/.c", ".hidden.py"]
INVALID = ["a.py", "pkg/a.py", "__init__.py", "a.env", "pkg/b.hidden"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        DOT_NAME,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", VALID)
def test_a_name_that_starts_with_a_dot_is_hidden(path) -> None:
    assert DOT_NAME(Path(path)) is True


@pytest.mark.parametrize("path", INVALID)
def test_other_names_are_not(path) -> None:
    assert DOT_NAME(Path(path)) is False


@pytest.mark.parametrize("path", [".cache/a.py", "pkg/.cache/a.py", ".git/hooks/pre-commit.py"])
def test_only_the_name_of_the_file_is_judged_not_its_folders(path) -> None:
    """A visible file in a hidden folder is not hidden by this rule; the strict exclusions look at folders."""
    assert DOT_NAME(Path(path)) is False
