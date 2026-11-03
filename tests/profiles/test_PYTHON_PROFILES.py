from simplibs.extractor import Profile
from simplibs.extractor_python.profiles import (
    PYTHON_CODE_CLEAN,
    PYTHON_CODE_NO_IMPORTS,
    PYTHON_DATA_ALL,
    PYTHON_OUTLINE,
    PYTHON_PROFILES,
    PYTHON_SRC_CLEAN,
)


def test_is_a_tuple_of_profiles() -> None:
    assert isinstance(PYTHON_PROFILES, tuple)
    assert all(isinstance(profile, Profile) for profile in PYTHON_PROFILES)


def test_holds_the_five_profiles_in_the_order_of_the_listing() -> None:
    assert PYTHON_PROFILES == (
        PYTHON_CODE_CLEAN,
        PYTHON_CODE_NO_IMPORTS,
        PYTHON_DATA_ALL,
        PYTHON_OUTLINE,
        PYTHON_SRC_CLEAN,
    )


def test_the_keys_in_the_order_of_the_listing() -> None:
    assert [profile.key for profile in PYTHON_PROFILES] == [
        "python/code-clean",
        "python/code-no-imports",
        "python/data-all",
        "python/outline",
        "python/src-clean",
    ]


def test_every_profile_belongs_to_the_system_python() -> None:
    assert {profile.system for profile in PYTHON_PROFILES} == {"python"}


def test_the_keys_are_unique() -> None:
    keys = [profile.key for profile in PYTHON_PROFILES]
    assert len(keys) == len(set(keys))


def test_the_output_names_are_unique() -> None:
    """Two profiles that wrote the same file would overwrite each other's output."""
    names = [profile.output_name for profile in PYTHON_PROFILES]
    assert len(names) == len(set(names))


def test_the_output_names_start_with_the_system() -> None:
    assert all(profile.output_name.startswith("python_") for profile in PYTHON_PROFILES)


def test_every_profile_has_a_description() -> None:
    assert all(profile.description.strip() for profile in PYTHON_PROFILES)


def test_the_profiles_are_in_the_listing_order_of_their_keys() -> None:
    keys = [profile.key for profile in PYTHON_PROFILES]
    assert keys == sorted(keys)
