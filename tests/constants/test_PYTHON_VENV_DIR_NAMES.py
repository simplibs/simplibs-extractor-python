from simplibs.extractor_python.constants import PYTHON_VENV_DIR_NAMES


def test_value() -> None:
    assert PYTHON_VENV_DIR_NAMES == ("venv", ".venv", "env", "virtualenv")


def test_is_a_tuple_of_strings() -> None:
    assert isinstance(PYTHON_VENV_DIR_NAMES, tuple)
    assert all(isinstance(name, str) for name in PYTHON_VENV_DIR_NAMES)


def test_no_name_is_listed_twice() -> None:
    assert len(PYTHON_VENV_DIR_NAMES) == len(set(PYTHON_VENV_DIR_NAMES))


def test_every_name_is_a_single_folder_name() -> None:
    for name in PYTHON_VENV_DIR_NAMES:
        assert name and name == name.strip(), name
        assert "/" not in name and "\\" not in name, name
        assert not any(char.isspace() for char in name), name


def test_the_hidden_and_the_visible_spelling_are_both_there() -> None:
    assert "venv" in PYTHON_VENV_DIR_NAMES
    assert ".venv" in PYTHON_VENV_DIR_NAMES
