from pathlib import Path
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.constants import PYTHON_OUTPUT_DIR_NAMES
from simplibs.extractor_python.file_rules import OUTPUT_DIRS

VALID = ["build/a.py", "dist/pkg/a.py", "pkg/out/a.py", "a/b/build/c/d.py"]
INVALID = ["a.py", "pkg/a.py", "building/a.py", "distribution/a.py", "outer/a.py", "build.py", "pkg/dist.py", "output/a.py"]


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        OUTPUT_DIRS,
        valid_values=[Path(path) for path in VALID],
        invalid_values=[Path(path) for path in INVALID],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("name", PYTHON_OUTPUT_DIR_NAMES)
def test_every_name_of_the_constant_is_a_build_folder(name) -> None:
    assert OUTPUT_DIRS(Path(name) / "a.py") is True
    assert OUTPUT_DIRS(Path("pkg") / name / "deep" / "a.py") is True


@pytest.mark.parametrize("path", INVALID)
def test_a_folder_name_is_compared_as_a_whole(path) -> None:
    """`building` is not `build`, and a FILE called `build.py` is not a folder."""
    assert OUTPUT_DIRS(Path(path)) is False
