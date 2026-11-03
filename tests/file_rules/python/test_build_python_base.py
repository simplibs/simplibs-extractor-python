from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.rules import Rule
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor_python.file_rules import build_python_base

ALWAYS_TAKEN = ["a.py", "pkg/a.py", "a/b/c/d.py", "__version__.py", "pkg/__about__.py"]
ALWAYS_LEFT_OUT = [
    "a.txt",
    "README.md",
    "pkg/a.pyi",
    "pkg/a.pyc",
    ".hidden.py",
    "pkg/.hidden.py",
    "__pycache__/a.py",
    "pkg/__pycache__/a.py",
    "__pypackages__/x/a.py",
]
INIT = ["__init__.py", "pkg/__init__.py"]
MAIN = ["__main__.py", "pkg/__main__.py"]


def _paths(*groups) -> list[Path]:
    return [Path(path) for group in groups for path in group]


def test_returns_a_rule() -> None:
    assert isinstance(build_python_base(), Rule)


@pytest.mark.parametrize(
    "include_init, include_main",
    [(True, True), (True, False), (False, True), (False, False)],
    ids=["both", "init-only", "main-only", "neither"],
)
def test_rule_contract(subtests, include_init, include_main) -> None:
    taken = [*ALWAYS_TAKEN, *(INIT if include_init else []), *(MAIN if include_main else [])]
    left_out = [*ALWAYS_LEFT_OUT, *([] if include_init else INIT), *([] if include_main else MAIN)]
    assert_rule_contract(
        subtests,
        build_python_base(include_init=include_init, include_main=include_main),
        valid_values=_paths(taken),
        invalid_values=_paths(left_out),
        check_slots=False,
        check_value=False,
        verbose=False,
    )


def test_the_defaults_take_the_package_files() -> None:
    """The old rule dropped every name that starts with two underscores; now both package files are taken."""
    rule = build_python_base()
    assert all(rule(path) is True for path in _paths(INIT, MAIN))


def test_other_dunder_names_are_ordinary_modules() -> None:
    rule = build_python_base(include_init=False, include_main=False)
    assert rule(Path("__version__.py")) is True
    assert rule(Path("pkg/__about__.py")) is True


def test_switching_the_init_off_leaves_the_main() -> None:
    rule = build_python_base(include_init=False)
    assert rule(Path("pkg/__init__.py")) is False
    assert rule(Path("pkg/__main__.py")) is True


def test_switching_the_main_off_leaves_the_init() -> None:
    rule = build_python_base(include_main=False)
    assert rule(Path("pkg/__main__.py")) is False
    assert rule(Path("pkg/__init__.py")) is True


def test_a_folder_with_two_underscores_is_still_left_out_with_both_files_on() -> None:
    rule = build_python_base()
    assert rule(Path("__pycache__/__init__.py")) is False


def test_every_call_builds_its_own_rule() -> None:
    assert build_python_base() is not build_python_base()


@pytest.mark.parametrize("option", ["include_init", "include_main"])
@pytest.mark.parametrize("value", ["yes", None, [True]])
def test_the_switches_must_be_bool(option, value) -> None:
    with pytest.raises(ValidationError):
        build_python_base(**{option: value})


def test_the_switches_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        build_python_base(True)  # type: ignore[misc]
