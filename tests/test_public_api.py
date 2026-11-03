import pytest
import simplibs.extractor_python as extractor_python
from pathlib import Path

EXPECTED = {
    # steps
    "python_comment_spans",
    "python_outline",
    "remove_python_comments",
    "remove_python_decorators",
    "remove_python_docstrings",
    "remove_python_imports",
    # add-on of the extractor
    "register_all",
    # types
    "OnError",
}

STEPS = [
    "python_comment_spans",
    "python_outline",
    "remove_python_comments",
    "remove_python_decorators",
    "remove_python_docstrings",
    "remove_python_imports",
]

# The four domain folders are public through their own `__all__`, not through the root.
DOMAINS = {
    "actions": {
        "PythonOutline",
        "RemovePythonComments",
        "RemovePythonDecorators",
        "RemovePythonDocstrings",
        "RemovePythonImports",
    },
    "file_rules": {
        "DOT_NAME",
        "INIT_NAME",
        "IN_DUNDER_DIR",
        "MAIN_NAME",
        "OUTPUT_DIRS",
        "VCS_DIRS",
        "VENV_DIRS",
        "PYTHON_BASE",
        "PYTHON_CONFIG",
        "PYTHON_STRICT_EXCLUDE",
        "PYTHON_TESTS",
        "build_python_base",
    },
    "presets": {
        "PYTHON_CLEAN",
        "PYTHON_NO_IMPORTS",
    },
    "profiles": {
        "PYTHON_CODE_CLEAN",
        "PYTHON_CODE_NO_IMPORTS",
        "PYTHON_DATA_ALL",
        "PYTHON_OUTLINE",
        "PYTHON_PROFILES",
        "PYTHON_SRC_CLEAN",
    },
}

SUBPACKAGES = {"annotations", "constants", "file_rules", "logic", "actions", "presets", "profiles", "plugin"}


def test_the_public_names_are_exactly_the_agreed_ones() -> None:
    """Adding or removing a public name is a decision; it must change this test on purpose."""
    assert set(extractor_python.__all__) == EXPECTED
    assert len(extractor_python.__all__) == 8


def test_no_name_is_listed_twice() -> None:
    assert len(extractor_python.__all__) == len(set(extractor_python.__all__))


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_every_public_name_exists(name) -> None:
    assert hasattr(extractor_python, name)


def test_a_star_import_brings_exactly_the_public_names() -> None:
    namespace: dict = {}
    exec("from simplibs.extractor_python import *", namespace)
    namespace.pop("__builtins__")
    assert set(namespace) == EXPECTED


def test_nothing_else_is_public() -> None:
    """Besides the public names, the package shows only its own sub-packages."""
    public = {name for name in dir(extractor_python) if not name.startswith("_")}
    assert public - set(extractor_python.__all__) <= SUBPACKAGES


@pytest.mark.parametrize("name", [*STEPS, "register_all"])
def test_the_steps_and_the_entry_point_are_callable(name) -> None:
    assert callable(getattr(extractor_python, name)), name


def test_the_steps_are_the_ones_of_the_logic_layer() -> None:
    import simplibs.extractor_python.logic as logic

    for name in STEPS:
        assert getattr(extractor_python, name) is getattr(logic, name), name


def test_on_error_is_the_two_agreed_words() -> None:
    import typing
    from simplibs.extractor_python import OnError

    assert typing.get_args(OnError) == ("raise", "keep")


# ---------------------------------------------------------------- the domain folders

@pytest.mark.parametrize("domain", sorted(DOMAINS))
def test_the_domain_has_exactly_the_agreed_names(domain) -> None:
    import importlib

    module = importlib.import_module(f"simplibs.extractor_python.{domain}")
    assert set(module.__all__) == DOMAINS[domain]
    assert len(module.__all__) == len(set(module.__all__)), "a name is listed twice"


@pytest.mark.parametrize("domain", sorted(DOMAINS))
def test_every_name_of_a_domain_exists(domain) -> None:
    import importlib

    module = importlib.import_module(f"simplibs.extractor_python.{domain}")
    for name in DOMAINS[domain]:
        assert hasattr(module, name), name


def test_the_root_does_not_re_export_the_domains() -> None:
    domain_names = set().union(*DOMAINS.values())
    assert domain_names & set(extractor_python.__all__) == set()


def test_the_domains_do_not_share_a_name_with_each_other_by_accident() -> None:
    """`DOT_NAME` and the like are listed once, in `file_rules`; no other domain repeats a name."""
    seen: dict[str, str] = {}
    repeated = []
    for domain, names in DOMAINS.items():
        for name in names:
            if name in seen:
                repeated.append(f"{name}: {seen[name]}, {domain}")
            seen[name] = domain
    assert repeated == []


# ---------------------------------------------------------------- the package as a whole

def test_the_package_is_marked_as_typed() -> None:
    assert (Path(extractor_python.__file__).parent / "py.typed").is_file()
