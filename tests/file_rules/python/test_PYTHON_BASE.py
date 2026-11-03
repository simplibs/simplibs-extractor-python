from pathlib import Path
import pytest
from simplibs.rules import Rule
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import PYTHON_BASE, build_python_base

TAKEN = ["a.py", "pkg/a.py", "pkg/__init__.py", "__main__.py", "pkg/__about__.py"]
LEFT_OUT = ["a.txt", "pkg/a.pyi", ".hidden.py", "__pycache__/a.py", "pkg/__pycache__/__init__.py"]


def test_is_a_rule() -> None:
    assert isinstance(PYTHON_BASE, Rule)


def test_rule_contract(subtests) -> None:
    assert_rule_contract(
        subtests,
        PYTHON_BASE,
        valid_values=[Path(path) for path in TAKEN],
        invalid_values=[Path(path) for path in LEFT_OUT],
        check_slots=False,
        check_value=False,
        verbose=False,
    )


@pytest.mark.parametrize("path", [*TAKEN, *LEFT_OUT])
def test_decides_like_the_builder_with_its_defaults(path) -> None:
    assert PYTHON_BASE(Path(path)) is build_python_base()(Path(path))


def test_takes_init_and_main() -> None:
    assert PYTHON_BASE(Path("pkg/__init__.py")) is True
    assert PYTHON_BASE(Path("pkg/__main__.py")) is True
