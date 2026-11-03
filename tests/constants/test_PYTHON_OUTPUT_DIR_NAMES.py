from simplibs.extractor_python.constants import PYTHON_OUTPUT_DIR_NAMES


def test_value() -> None:
    assert PYTHON_OUTPUT_DIR_NAMES == ("build", "dist", "out")


def test_is_a_tuple_of_strings() -> None:
    assert isinstance(PYTHON_OUTPUT_DIR_NAMES, tuple)
    assert all(isinstance(name, str) for name in PYTHON_OUTPUT_DIR_NAMES)


def test_no_name_is_listed_twice() -> None:
    assert len(PYTHON_OUTPUT_DIR_NAMES) == len(set(PYTHON_OUTPUT_DIR_NAMES))


def test_every_name_is_a_single_folder_name() -> None:
    """A folder is compared as a whole name, so a name holds no separator and no whitespace."""
    for name in PYTHON_OUTPUT_DIR_NAMES:
        assert name and name == name.strip(), name
        assert "/" not in name and "\\" not in name, name
        assert not any(char.isspace() for char in name), name
