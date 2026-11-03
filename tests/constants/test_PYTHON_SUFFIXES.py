from simplibs.extractor.definitions._helpers import is_suffix_key
from simplibs.extractor_python.constants import PYTHON_SUFFIXES


def test_value() -> None:
    assert PYTHON_SUFFIXES == (".py",)


def test_is_a_tuple_of_strings() -> None:
    assert isinstance(PYTHON_SUFFIXES, tuple)
    assert all(isinstance(suffix, str) for suffix in PYTHON_SUFFIXES)


def test_stub_and_windows_script_suffixes_are_not_source() -> None:
    """A stub repeats the signatures of a module that is in the output anyway."""
    assert ".pyi" not in PYTHON_SUFFIXES
    assert ".pyw" not in PYTHON_SUFFIXES


def test_every_suffix_is_a_valid_key_of_a_steps_mapping() -> None:
    """The profiles use the suffixes as keys of `by_suffix`, so each one must be a lowercase suffix with a dot."""
    for suffix in PYTHON_SUFFIXES:
        assert is_suffix_key(suffix), suffix
        assert suffix != "*", suffix
