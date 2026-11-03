# 🔌 `plugin` — The Meeting Point With the Extractor

The `simplibs-extractor` knows **no language** — on its own it has only the profile `generic/all`. This library is an
**add-on**: the package that tells the extractor what a Python project looks like. The `plugin` package is where the two
meet. It holds one function, `register_all`, which puts the five profiles into the extractor's registry.

```
pip install simplibs-extractor-python
        │
        ▼
 entry point in the group "simplibs.extractor.plugins"
        │      python = "simplibs.extractor_python:register_all"
        ▼
 load_plugins() ──► calls register_all() ──► register_profile(...)  ──►  the registry of the extractor
```

`pip install` is the whole installation. The entry point is written in this library's own `pyproject.toml`:

```toml
[project.entry-points."simplibs.extractor.plugins"]
python = "simplibs.extractor_python:register_all"
```

Nothing has to be imported by name; the next `simplibs-extractor --list-systems` already shows the system `python`.

## Using the add-on

| Where you work       | What you do                                                                                              |
|----------------------|----------------------------------------------------------------------------------------------------------|
| **the command line** | Nothing. The command loads add-ons itself, before its parser is built; one that fails to load is a **warning**, not a stop. |
| **Python**           | Call `load_plugins()` of the extractor once, before you look a profile up — or call `register_all()` yourself. `extract()` does **not** load add-ons by itself. |

```python
from simplibs.extractor import extract, list_systems, load_plugins

list_systems()                                           # -> ['generic']
loaded, failed = load_plugins()                          # every installed add-on registers its profiles
loaded                                                   # -> ['python']      with this library installed
list_systems()                                           # -> ['generic', 'python']

extract(source="my_project", profile="python/src-clean")
```

## The rules of an add-on function, and how `register_all` keeps them

| Rule                                                      | How `register_all` meets it                                           |
|-----------------------------------------------------------|-----------------------------------------------------------------------|
| Takes **no required argument**.                           | Its only parameter is the optional, keyword-only `replace_existing`.  |
| Registers with **`replace_existing=True`**.               | That is the default: calling it twice changes nothing.                |
| Only **registers** — no scanning, no network, no printing.| It walks a tuple of ready objects and calls `register_profile`.       |
| Uses the **public API** only.                             | `Profile` and `register_profile` of `simplibs.extractor`.             |
| Stays **quick and quiet**.                                | Five objects built at import time; nothing is computed in the call.   |

---

## 🧭 Table of Contents

* [`register_all`](#register_all)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-plugin--the-meeting-point-with-the-extractor)

---

### `register_all`

**Registers every profile of this library in the registry of the extractor.**

The extractor calls it, with no arguments, for every installed add-on (the entry-point group
`simplibs.extractor.plugins`).

**Parameters:**

| Name               | Type   | Default | Description                                                                                       |
|--------------------|--------|---------|---------------------------------------------------------------------------------------------------|
| `replace_existing` | `bool` | `True`  | Replace a profile that already has the key — the default, so calling it twice changes nothing. *(keyword-only)* |

**Returns:** `list[str]` — the keys of the registered profiles, in the order of
[`PYTHON_PROFILES`](README_EXTRACTOR_PYTHON_PROFILES.md#python_profiles).

**Raises:**

* `AlreadyExistsError` (`EXTRACTOR_PROFILE_EXISTS`) — the card of `register_profile`: a key is taken and
  `replace_existing` is `False`.
* `ValidationError` — `replace_existing` is not a `bool`.

**Example usage:**

```python
from simplibs.extractor_python import register_all

register_all()
# -> ['python/code-clean', 'python/code-no-imports', 'python/data-all', 'python/outline', 'python/src-clean']

register_all()                                           # the same list again; nothing changed, nothing failed

register_all(replace_existing=False)                     # raises — the keys are taken now
```

**Why `replace_existing=True`.** `load_plugins()` may run more than once — a second command in one process, a reload, a
test. Without it the second call would find the keys taken and the add-on would land in `failed`.

**Profiles you register yourself.** `register_all` knows only the five profiles of this library. A profile of your own is
registered with `register_profile` from your own code (see
[a profile of your own](README_EXTRACTOR_PYTHON_PROFILES.md#a-profile-of-your-own)); it is not touched by this function.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def register_all(*, replace_existing: bool = True) -> list[str]:

    # 1. Register each profile
    keys: list[str] = []
    for profile in PYTHON_PROFILES:
        registered = register_profile(profile, replace_existing=replace_existing)
        keys.append(registered.key)

    return keys
```

`register_profile` returns the profile it registered, and the profile knows its `key` (`"system/name"`) — so the function
collects the keys from what was registered, not from what it meant to register. The registry then answers
`--list-profiles python`; the list of profiles is the only thing the add-on has to say.

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

This package raises **no cards of its own**. The one card that can come out of `register_all` is the card of the
extractor's registry (`EXTRACTOR_PROFILE_EXISTS`), and only with `replace_existing=False`.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-plugin--the-meeting-point-with-the-extractor)
