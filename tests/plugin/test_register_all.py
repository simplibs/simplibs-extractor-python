import pytest
from simplibs.exception import AlreadyExistsError, ValidationError
from simplibs.extractor.registry import get_profile
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY, RENDERER_REGISTRY
from simplibs.extractor_python.plugin import register_all
from simplibs.extractor_python.profiles import PYTHON_PROFILES

KEYS = [profile.key for profile in PYTHON_PROFILES]


@pytest.fixture(autouse=True)
def without_the_python_profiles():
    """Start from a registry that does not know the add-on yet, whatever was loaded before."""
    for key in KEYS:
        PROFILE_REGISTRY.pop(key, None)


def test_returns_the_keys_of_the_profiles_in_order() -> None:
    assert register_all() == KEYS


def test_every_profile_is_registered_under_its_key() -> None:
    register_all()
    for profile in PYTHON_PROFILES:
        assert get_profile(profile.key) is profile


def test_only_the_profiles_of_the_add_on_are_added() -> None:
    before = set(PROFILE_REGISTRY)
    register_all()
    assert set(PROFILE_REGISTRY) - before == set(KEYS)
    assert before <= set(PROFILE_REGISTRY)


def test_no_renderer_is_touched() -> None:
    before = dict(RENDERER_REGISTRY)
    register_all()
    assert dict(RENDERER_REGISTRY) == before


def test_a_second_call_changes_nothing_and_does_not_fail() -> None:
    first = register_all()
    snapshot = dict(PROFILE_REGISTRY)
    second = register_all()
    assert second == first
    assert dict(PROFILE_REGISTRY) == snapshot


def test_a_profile_that_already_has_the_key_is_replaced_by_default() -> None:
    from simplibs.extractor import Profile

    PROFILE_REGISTRY[KEYS[0]] = Profile("python", KEYS[0].split("/")[1], description="somebody else")
    register_all()
    assert get_profile(KEYS[0]) is PYTHON_PROFILES[0]


def test_replace_existing_false_works_on_a_free_registry() -> None:
    assert register_all(replace_existing=False) == KEYS


def test_replace_existing_false_refuses_a_taken_key() -> None:
    """The docstring of `register_all` names `StateError`; the extractor raises its more specific card."""
    register_all()
    with pytest.raises(AlreadyExistsError):
        register_all(replace_existing=False)


@pytest.mark.parametrize("value", ["yes", None, 1, "False"])
def test_replace_existing_must_be_a_bool(value) -> None:
    with pytest.raises(ValidationError):
        register_all(replace_existing=value)


def test_replace_existing_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        register_all(True)  # type: ignore[misc]


def test_it_needs_no_argument() -> None:
    """The extractor calls every add-on with nothing."""
    assert isinstance(register_all(), list)


def test_it_prints_nothing(capsys) -> None:
    register_all()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
