# 📋 `profiles` — The Five Profiles

A **profile** is a name for "which files, how to clean them, what the output is called": rules on the path plus steps
that transform each file's text. The `profiles` package holds the five profiles of the system `python` as ordinary
`Profile` objects of [`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/).

```bash
simplibs-extractor python src-clean my_project
simplibs-extractor python code-clean,data-all my_project         # two profiles -> two files, one run
```

Registering them is the job of [`register_all`](README_EXTRACTOR_PYTHON_PLUGIN.md#register_all) — it runs by itself
when the extractor finds this add-on. Having them as **objects** lets a program use one directly or build its own on top
of it:

```python
from dataclasses import replace
from simplibs.extractor import extract, register_profile
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN

mine = replace(PYTHON_SRC_CLEAN, name="mine", output_name="mine.md")      # a changed copy; the original is untouched
register_profile(mine)

extract(source="my_project", profile="python/mine")
```

The package has its own `__all__` and is **not** re-exported from the package root.

## Which profile when

| Profile                  | Output                      | Files                                                | What happens to the text                                  |
|--------------------------|-----------------------------|------------------------------------------------------|-----------------------------------------------------------|
| `python/data-all`        | `python_data_all.md`        | every relevant `.py` file                            | nothing — as it is                                        |
| `python/code-clean`      | `python_code_clean.md`      | every relevant `.py` file                            | comments, docstrings and extra blank lines out; imports stay |
| `python/code-no-imports` | `python_code_no_imports.md` | every relevant `.py` file                            | comments, docstrings, imports, decorators and blank lines out |
| `python/src-clean`       | `python_src_clean.md`       | like `code-clean`, **without** tests, configuration, environments and build folders | as `code-clean` |
| `python/outline`         | `python_outline.md`         | every relevant `.py` file                            | signatures without bodies                                 |

"Every relevant `.py` file" is [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base): Python files, with
`__init__.py` and `__main__.py`, without dot files and without folders such as `__pycache__`.

## One file, five profiles

The file `src/app.py` of a small project (431 bytes):

```python
"""Tiny demo app."""
import os
from pathlib import Path

# Where the data lives.
DATA = Path("data")  # relative


@cache(60)
def load(name: str, *, strict: bool = False) -> str:
    """Read one file.

    Raises if strict and missing.
    """
    path = DATA / name  # build the path
    return path.read_text()


class Store:
    """Keeps loaded files."""

    def __init__(self) -> None:
        self.items: dict[str, str] = {}
```

`python/code-clean` and `python/src-clean` (the same steps) — **259 bytes**:

```python
import os
from pathlib import Path

DATA = Path("data")

@cache(60)
def load(name: str, *, strict: bool = False) -> str:
    path = DATA / name
    return path.read_text()

class Store:

    def __init__(self) -> None:
        self.items: dict[str, str] = {}
```

`python/code-no-imports` — **209 bytes**:

```python
DATA = Path("data")
def load(name: str, *, strict: bool = False) -> str:
    path = DATA / name
    return path.read_text()
class Store:
    def __init__(self) -> None:
        self.items: dict[str, str] = {}
```

`python/outline` — **156 bytes**:

```python
@cache(60)
def load(name: str, *, strict: bool=False) -> str: ...  # Read one file.
class Store:  # Keeps loaded files.
    def __init__(self) -> None: ...
```

`python/data-all` gives the file back as it is (431 bytes). The report of a run shows the same numbers file by file
(`bytes_in` → `bytes_out` of each `FileReport`).

## A file that is not valid Python

The profiles with steps (`code-clean`, `code-no-imports`, `src-clean`, `outline`) read the source with `ast` or
`tokenize`. A file that cannot be read — an old Python 2 file, a half-written module — makes **that file** an `error` in
the report with the reason, the other files are not affected, and the run is unsuccessful. `python/data-all` has no steps
and cannot fail on a file.

To get such a file into the output unchanged instead, build a profile of your own with `on_error="keep"` (see
[the last section](#a-profile-of-your-own)).

---

## 🧭 Table of Contents

* [`PYTHON_CODE_CLEAN`](#python_code_clean)
* [`PYTHON_CODE_NO_IMPORTS`](#python_code_no_imports)
* [`PYTHON_DATA_ALL`](#python_data_all)
* [`PYTHON_OUTLINE`](#python_outline)
* [`PYTHON_SRC_CLEAN`](#python_src_clean)
* [`PYTHON_PROFILES`](#python_profiles)
* [A profile of your own](#a-profile-of-your-own)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-profiles--the-five-profiles)

---

### `PYTHON_CODE_CLEAN`

**The profile `python/code-clean`:** the code with its prose taken away.

**Fields:**

| Field         | Value                                                                                          |
|---------------|------------------------------------------------------------------------------------------------|
| `system`      | `"python"`                                                                                     |
| `name`        | `"code-clean"`                                                                                 |
| `description` | `"Python without comments, docstrings and extra blank lines (imports stay)"`                   |
| `include`     | [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base)                             |
| `exclude`     | *(none)*                                                                                       |
| `steps`       | [`PYTHON_CLEAN`](README_EXTRACTOR_PYTHON_PRESETS.md#python_clean) for the suffix `.py`         |
| `output_name` | `"python_code_clean.md"`                                                                       |

**Example usage:**

```python
from simplibs.extractor import extract

result = extract(source="my_project", profile="python/code-clean")
result.target                                            # -> my_project/python_code_clean.md
[(f.relative, f.bytes_in, f.bytes_out) for f in result.ok_files]       # what the profile saved, file by file
```

The tests, the configuration and the build folders are **in** the output — see
[`PYTHON_SRC_CLEAN`](#python_src_clean) for the strict one.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_CODE_CLEAN: Final[Profile] = Profile(
    system="python",
    name="code-clean",
    description="Python without comments, docstrings and extra blank lines (imports stay)",
    include=PYTHON_BASE,
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_code_clean.md",
)
```

`by_suffix` of `simplibs-extractor` gives the preset to the files of the listed suffixes. A file that is not valid
Python makes **that** file an `error`; the others are not affected.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_CODE_NO_IMPORTS`

**The profile `python/code-no-imports`:** pure logic — what the code does, not what it is wired to.

**Fields:**

| Field         | Value                                                                                          |
|---------------|------------------------------------------------------------------------------------------------|
| `system`      | `"python"`                                                                                     |
| `name`        | `"code-no-imports"`                                                                            |
| `description` | `"Pure logic: no imports, decorators, comments, docstrings or blank lines"`                    |
| `include`     | [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base)                             |
| `exclude`     | *(none)*                                                                                       |
| `steps`       | [`PYTHON_NO_IMPORTS`](README_EXTRACTOR_PYTHON_PRESETS.md#python_no_imports) for the suffix `.py` |
| `output_name` | `"python_code_no_imports.md"`                                                                  |

**Example usage:**

```bash
simplibs-extractor python code-no-imports my_project           # -> my_project/python_code_no_imports.md
```

The output is **for reading, not for running**: the names that were imported are still used further down, and a
decorator that changed what a function *is* is gone.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_CODE_NO_IMPORTS: Final[Profile] = Profile(
    system="python",
    name="code-no-imports",
    description="Pure logic: no imports, decorators, comments, docstrings or blank lines",
    include=PYTHON_BASE,
    steps=by_suffix(PYTHON_NO_IMPORTS, PYTHON_SUFFIXES),
    output_name="python_code_no_imports.md",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_DATA_ALL`

**The profile `python/data-all`:** every relevant Python file, as it is.

The files selected by `PYTHON_BASE` and **no transformation**. A file that is not valid Python cannot fail here.

**Fields:**

| Field         | Value                                                                  |
|---------------|------------------------------------------------------------------------|
| `system`      | `"python"`                                                             |
| `name`        | `"data-all"`                                                           |
| `description` | `"Every relevant .py file, as it is"`                                  |
| `include`     | [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base)     |
| `exclude`     | *(none)*                                                               |
| `steps`       | *(none)*                                                               |
| `output_name` | `"python_data_all.md"`                                                 |

**Example usage:**

```bash
simplibs-extractor python data-all my_project --dry-run        # plan and report, write nothing
```

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_DATA_ALL: Final[Profile] = Profile(
    system="python",
    name="data-all",
    description="Every relevant .py file, as it is",
    include=PYTHON_BASE,
    output_name="python_data_all.md",
)
```

No `steps`: the extractor takes the text of each file and changes nothing.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_OUTLINE`

**The profile `python/outline`:** an overview of classes and functions — signatures without bodies.

New in this library: what a project offers, in a fraction of the size. For a reader with a limited window the signatures
are most of what is needed to ask the right questions. Each file of the output is **valid Python** again.

**Fields:**

| Field         | Value                                                                                          |
|---------------|------------------------------------------------------------------------------------------------|
| `system`      | `"python"`                                                                                     |
| `name`        | `"outline"`                                                                                    |
| `description` | `"Overview of classes and functions: signatures without bodies"`                               |
| `include`     | [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base)                             |
| `exclude`     | *(none)*                                                                                       |
| `steps`       | [`PythonOutline()`](README_EXTRACTOR_PYTHON_ACTIONS.md#pythonoutline) for the suffix `.py`     |
| `output_name` | `"python_outline.md"`                                                                          |

**Example usage:**

```bash
simplibs-extractor python outline my_project                    # -> my_project/python_outline.md
```

A file that defines no class and no function (a package's empty `__init__.py`) gives an **empty** text.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_OUTLINE: Final[Profile] = Profile(
    system="python",
    name="outline",
    description="Overview of classes and functions: signatures without bodies",
    include=PYTHON_BASE,
    steps=by_suffix(PythonOutline(), PYTHON_SUFFIXES),
    output_name="python_outline.md",
)
```

`PythonOutline()` with its defaults: the first line of each docstring stays as a trailing comment. For a bare outline
build your own profile with `PythonOutline(docstrings=False)`.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_SRC_CLEAN`

**The profile `python/src-clean`:** like `code-clean`, without tests, configuration, environments and build folders —
only what the project does.

The old strict file filter made visible: the old code defined it and no profile ever used it.

**Fields:**

| Field         | Value                                                                                          |
|---------------|------------------------------------------------------------------------------------------------|
| `system`      | `"python"`                                                                                     |
| `name`        | `"src-clean"`                                                                                  |
| `description` | `"Like code-clean, without tests, configuration, environments and build folders"`              |
| `include`     | [`PYTHON_BASE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_base)                             |
| `exclude`     | [`PYTHON_STRICT_EXCLUDE`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_strict_exclude)         |
| `steps`       | [`PYTHON_CLEAN`](README_EXTRACTOR_PYTHON_PRESETS.md#python_clean) for the suffix `.py`         |
| `output_name` | `"python_src_clean.md"`                                                                        |

**Example usage:**

```python
from simplibs.extractor import extract

result = extract(source="my_project", profile="python/src-clean")
[f.relative for f in result.ok_files]                    # -> ['src/app.py', 'src/config.py']      no test_*.py, no setup.py
```

A folder called `env` that is something else (a settings package, say) is left out too — see the
[known limit](README_EXTRACTOR_PYTHON_CONSTANTS.md#python_venv_dir_names).

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_SRC_CLEAN: Final[Profile] = Profile(
    system="python",
    name="src-clean",
    description="Like code-clean, without tests, configuration, environments and build folders",
    include=PYTHON_BASE,
    exclude=PYTHON_STRICT_EXCLUDE,
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_src_clean.md",
)
```

The only difference from `PYTHON_CODE_CLEAN` is the `exclude` and the output name. A `config` of one `extract` call can
only narrow these rules further (`include` by AND, `exclude` by OR), never widen them.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_PROFILES`

**The profiles of the system `python`**, in the order the listing commands show them.

**Kind:** `tuple[Profile, ...]`.

**Example usage:**

```python
from simplibs.extractor_python.profiles import PYTHON_PROFILES

[profile.key for profile in PYTHON_PROFILES]
# -> ['python/code-clean', 'python/code-no-imports', 'python/data-all', 'python/outline', 'python/src-clean']
```

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_PROFILES: Final[tuple[Profile, ...]] = (
    PYTHON_CODE_CLEAN,
    PYTHON_CODE_NO_IMPORTS,
    PYTHON_DATA_ALL,
    PYTHON_OUTLINE,
    PYTHON_SRC_CLEAN,
)
```

`register_all` walks this tuple and registers each profile; add a profile to the system by adding it here.

</details>

[▲ Back to top](#-table-of-contents)

---

## A profile of your own

A profile is built from the parts in this library. Rules combine with `&`, `|` and `~`; steps chain with `>>`.

```python
from simplibs.extractor import Profile, by_suffix, register_profile
from simplibs.extractor_python.actions import PythonOutline, RemovePythonComments
from simplibs.extractor_python.constants import PYTHON_SUFFIXES
from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_TESTS
from simplibs.extractor_python.presets import PYTHON_CLEAN

# only the tests, cleaned
register_profile(Profile(
    system="python", name="tests-clean",
    description="The tests, without comments and docstrings",
    include=PYTHON_BASE & PYTHON_TESTS,
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_tests_clean.md",
))

# a bare outline, and a file that is not valid Python stays as it is
register_profile(Profile(
    system="python", name="outline-bare",
    description="Signatures only, no docstring notes; unreadable files unchanged",
    include=PYTHON_BASE,
    steps=by_suffix(PythonOutline(docstrings=False, on_error="keep"), PYTHON_SUFFIXES),
    output_name="python_outline_bare.md",
))
```

---

## Errors of this package

This package raises **no cards of its own**: the profiles are plain objects, built when the package is imported. A
profile that cannot work is refused by `Profile` itself (`EXTRACTOR_PROFILE_INVALID`); a file that cannot be read is an
`error` line in the result, not an exception.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-profiles--the-five-profiles)
