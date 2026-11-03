from pathlib import Path
import pytest
from simplibs.path import IGNORE_VCS
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import VCS_DIRS

VALID = [".git/config", ".git/hooks/a.py", "pkg/.git/a", ".svn/a.py", ".hg/a.py", ".bzr/a.py"]
INVALID = [
    "a.py",
    "pkg/a.py",
    ".gitignore",
    ".github/workflows/ci.yml",
    "git/a.py",
    "pkg/.gitkeep",
    "node_modules/a.js",
    "tmp/a.py",
]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        VCS_DIRS,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("name", sorted(IGNORE_VCS))
def test_every_name_of_the_list_of_simplibs_path_is_taken(name) -> None:
    """The names are not kept here: the library borrows `IGNORE_VCS`, the same for every language."""
    assert VCS_DIRS(Path(name) / "a") is True
    assert VCS_DIRS(Path("pkg") / name / "a") is True


@pytest.mark.parametrize("path", INVALID)
def test_a_folder_name_is_compared_as_a_whole(path) -> None:
    """`.github` is not `.git`; a file `.gitignore` is not a folder; `node_modules` and `tmp` are not version control."""
    assert VCS_DIRS(Path(path)) is False
