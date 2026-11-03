from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import PYTHON_TESTS

BY_NAME = ["test_a.py", "a_test.py", "a_tests.py", "tests.py", "test.py", "conftest.py", "pkg/test_x.py", "pkg/x_test.py"]
BY_FOLDER = ["tests/anything.py", "pkg/tests/helpers.py", "tests/sub/a.py", "test/a.py", "a/b/tests/c/d.py"]
INVALID = [
    "a.py",
    "pkg/a.py",
    "__init__.py",
    "latest_data.py",
    "contest.py",
    "attest.py",
    "testing.py",
    "my_conftest.py",
    "test_a.txt",
    "a_test.pyc",
    "conftest.pyi",
    "pkg/contest/a.py",
    "pkg/latest/a.py",
    "pkg/testsuite/a.py",
    "pkg/test_dir/a.py",
]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        PYTHON_TESTS,
        valid_values=[Path(path) for path in [*BY_NAME, *BY_FOLDER]],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", BY_NAME)
def test_a_test_is_recognised_by_its_name(path) -> None:
    assert PYTHON_TESTS(Path(path)) is True


@pytest.mark.parametrize("path", BY_FOLDER)
def test_a_test_is_recognised_by_its_folder(path) -> None:
    """Every file in a folder called `tests` or `test` is a test helper at least, whatever it is called."""
    assert PYTHON_TESTS(Path(path)) is True


@pytest.mark.parametrize("path", INVALID)
def test_a_piece_of_a_name_is_not_enough(path) -> None:
    """The old rule asked whether the path CONTAINED `test`; the pattern is anchored at both ends."""
    assert PYTHON_TESTS(Path(path)) is False


@pytest.mark.parametrize("path", ["latest_data.py", "contest.py", "attest.py"])
def test_the_files_the_old_rule_threw_away_stay(path) -> None:
    assert PYTHON_TESTS(Path(path)) is False
