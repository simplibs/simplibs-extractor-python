from simplibs.extractor import register_profile
from simplibs.validate import validate_call
# Outers
from ..profiles import PYTHON_PROFILES


@validate_call
def register_all(*, replace_existing: bool = True) -> list[str]:
    """Register every profile of this library in the registry of the extractor.

    The extractor calls it, with no arguments, for every installed add-on
    (entry-point group `simplibs.extractor.plugins`).

    Args:
        replace_existing: Replace a profile that already has the key (the default, so calling it twice changes nothing).

    Returns:
        The keys of the registered profiles (`"python/code-clean"`...).

    Raises:
        StateError: A key is taken and `replace_existing` is `False`.
    """

    # 1. Register each profile
    keys: list[str] = []
    for profile in PYTHON_PROFILES:
        registered = register_profile(profile, replace_existing=replace_existing)
        keys.append(registered.key)

    return keys


_DESIGN_NOTES = """
# register_all — What the Entry Point Calls

## Purpose
`pip install simplibs-extractor-python` is the whole installation: the entry
point `python = "simplibs.extractor_python:register_all"` makes the extractor
find this function, and the five profiles appear in `--list-systems`.

## The Rules of an Add-On Function
It takes no required argument, registers with `replace_existing=True`, only
registers (no scanning, no network, no printing) and uses only the public API
of the extractor (`Profile`, `register_profile`).
"""
