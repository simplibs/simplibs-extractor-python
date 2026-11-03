from simplibs.extractor_python.constants import PYTHON_CONFIG_NAMES


def test_value() -> None:
    assert PYTHON_CONFIG_NAMES == (
        "setup.py",
        "setup.cfg",
        "pyproject.toml",
        "Pipfile",
        "Pipfile.lock",
        "requirements.txt",
        "tox.ini",
        "pytest.ini",
    )


def test_is_a_tuple_of_strings() -> None:
    assert isinstance(PYTHON_CONFIG_NAMES, tuple)
    assert all(isinstance(name, str) for name in PYTHON_CONFIG_NAMES)


def test_no_name_is_listed_twice() -> None:
    assert len(PYTHON_CONFIG_NAMES) == len(set(PYTHON_CONFIG_NAMES))


def test_every_name_is_a_plain_file_name() -> None:
    """A name is compared with the name of a file, so it holds no folder and no whitespace."""
    for name in PYTHON_CONFIG_NAMES:
        assert name and name == name.strip(), name
        assert "/" not in name and "\\" not in name, name
        assert not any(char.isspace() for char in name), name


def test_names_are_written_the_way_their_tools_write_them() -> None:
    """They are compared exactly, so `Pipfile` keeps its capital letter."""
    assert "Pipfile" in PYTHON_CONFIG_NAMES
    assert "pipfile" not in PYTHON_CONFIG_NAMES
