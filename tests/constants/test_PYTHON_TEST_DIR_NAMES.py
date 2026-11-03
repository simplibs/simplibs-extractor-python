from simplibs.extractor_python.constants import PYTHON_TEST_DIR_NAMES


def test_value() -> None:
    assert PYTHON_TEST_DIR_NAMES == ("tests", "test")


def test_is_a_tuple_of_strings() -> None:
    assert isinstance(PYTHON_TEST_DIR_NAMES, tuple)
    assert all(isinstance(name, str) for name in PYTHON_TEST_DIR_NAMES)


def test_no_name_is_listed_twice() -> None:
    assert len(PYTHON_TEST_DIR_NAMES) == len(set(PYTHON_TEST_DIR_NAMES))


def test_every_name_is_a_whole_folder_name() -> None:
    """Names are compared as a whole (`contest` is not `test`), so none holds a separator or whitespace."""
    for name in PYTHON_TEST_DIR_NAMES:
        assert name and name == name.strip(), name
        assert "/" not in name and "\\" not in name, name
        assert not any(char.isspace() for char in name), name
