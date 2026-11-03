# 📐 `file_rules` — Which Files Are Worth Reading

The `file_rules` package holds **rules on the path of a file** — the path **inside** the source folder, not the
absolute one. The profiles use them as `include` and `exclude`; they are ordinary `Rule` objects of
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/), so a program can compose its own selection from them with
`&`, `|` and `~`.

```python
from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_TESTS

only_tests = PYTHON_BASE & PYTHON_TESTS                 # Python files that are tests
no_tests = PYTHON_BASE & ~PYTHON_TESTS                  # Python files that are not
```

The package has its own `__all__` and is **not** re-exported from the package root — a rule and a step are different
kinds of thing and stay visibly different at the import line.

## Two groups

| Group    | What it holds                                                                                              |
|----------|------------------------------------------------------------------------------------------------------------|
| `atomic` | The shared pieces — **one rule, one idea**: a dot name, `__init__.py`, `__main__.py`, a folder of `__pycache__` kind, version control, environments, build output. |
| `python` | The rules of a Python project, **combined** from the atomic ones: the base choice, tests, configuration, the strict exclusion. |

`atomic` ← `python`: the second only combines what the first defines.

## How a rule is used

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_STRICT_EXCLUDE

PYTHON_BASE.is_valid(Path("src/app.py"))                # -> True
PYTHON_BASE.is_valid(Path("src/__pycache__/app.py"))    # -> False
PYTHON_STRICT_EXCLUDE.is_valid(Path("tests/test_a.py")) # -> True    "this file is one of those"
```

In a profile the pair works like this: `include=PYTHON_BASE` says what **may** enter, `exclude=PYTHON_STRICT_EXCLUDE` says
what **may not**. The extractor judges the path relative to the source, so a project that merely lies inside a folder
called `tests` is not dropped as "a test".

## Which path passes

The two ends of the scale — the base choice (`python/code-clean`) and the strict one (`python/src-clean`):

| Path                         | `PYTHON_BASE` | `PYTHON_TESTS` | `PYTHON_STRICT_EXCLUDE` | Taken by `src-clean`? |
|------------------------------|:-------------:|:--------------:|:-----------------------:|:---------------------:|
| `src/app.py`                 | ✅            |                |                         | ✅                    |
| `src/__init__.py`            | ✅            |                |                         | ✅                    |
| `src/__version__.py`         | ✅            |                |                         | ✅                    |
| `src/latest_data.py`         | ✅            |                |                         | ✅                    |
| `src/test_app.py`            | ✅            | ✅             | ✅                      |                       |
| `tests/helpers.py`           | ✅            | ✅             | ✅                      |                       |
| `conftest.py`                | ✅            | ✅             | ✅                      |                       |
| `setup.py`                   | ✅            |                | ✅                      |                       |
| `env/settings.py`            | ✅            |                | ✅                      |                       |
| `build/lib/app.py`           | ✅            |                | ✅                      |                       |
| `src/.hidden.py`             |               |                |                         |                       |
| `src/__pycache__/app.py`     |               |                |                         |                       |
| `README.md`, `stubs/app.pyi` |               |                |                         |                       |

The extractor's scan normally skips housekeeping folders (version control, virtual environments, ...) before a rule
sees them. The strict rules are a second fence for the case that the scan was told otherwise.

---

## 🧭 Table of Contents

**`atomic/` — the shared pieces**

* [`DOT_NAME`](#dot_name)
* [`INIT_NAME`](#init_name)
* [`MAIN_NAME`](#main_name)
* [`IN_DUNDER_DIR`](#in_dunder_dir)
* [`VCS_DIRS`](#vcs_dirs)
* [`VENV_DIRS`](#venv_dirs)
* [`OUTPUT_DIRS`](#output_dirs)

**`python/` — the rules of a Python project**

* [`PYTHON_BASE`](#python_base)
* [`build_python_base`](#build_python_base)
* [`PYTHON_TESTS`](#python_tests)
* [`PYTHON_CONFIG`](#python_config)
* [`PYTHON_STRICT_EXCLUDE`](#python_strict_exclude)

[⬅️ Back to main README](../README.md#-file_rules--which-files-are-worth-reading)

---

## `atomic/` — the shared pieces

Every piece is **one rule of one idea**. The rules about folders use `AnyParentNameIs` of
[`simplibs-path`](https://pypi.org/project/simplibs-path/) (some folder **above** the file satisfies a rule) and `IsIn`
of `simplibs-rules` (a name is one of a set, compared as a whole).

### `DOT_NAME`

**The file name starts with a dot** (`.env`, `.hidden.py`).

Dot files are settings and tool state, not source. Used by the base rule.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import DOT_NAME

DOT_NAME.is_valid(Path(".env"))                          # -> True
DOT_NAME.is_valid(Path("src/.hidden.py"))                # -> True
DOT_NAME.is_valid(Path("src/app.py"))                    # -> False
DOT_NAME.is_valid(Path(".cache/app.py"))                 # -> False    only the NAME is judged
```

**Name only.** A visible file inside a `.cache` folder is not hidden by this rule; the strict exclusions look at
folders.

<details>
<summary>🔍 Under the hood</summary>

```python
DOT_NAME: Final[Rule] = NameIs(StartsWith("."))
```

`NameIs` points a string rule (`StartsWith`) at the final name of the path.

</details>

[▲ Back to top](#-table-of-contents)

---

### `INIT_NAME`

**The file is called `__init__.py`.**

`__init__.py` holds the public names and `__all__` of a package, so it is usually the best single file for understanding
one. The base rule takes it unless `include_init=False`.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import INIT_NAME

INIT_NAME.is_valid(Path("src/__init__.py"))              # -> True
INIT_NAME.is_valid(Path("__init__.py"))                  # -> True
INIT_NAME.is_valid(Path("src/__main__.py"))              # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
INIT_NAME: Final[Rule] = NameIs(Equals("__init__.py"))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `MAIN_NAME`

**The file is called `__main__.py`.**

What runs with `python -m package` — the entry point of a package. The base rule takes it unless `include_main=False`.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import MAIN_NAME

MAIN_NAME.is_valid(Path("pkg/__main__.py"))              # -> True
MAIN_NAME.is_valid(Path("pkg/main.py"))                  # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
MAIN_NAME: Final[Rule] = NameIs(Equals("__main__.py"))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `IN_DUNDER_DIR`

**Some folder above the file has a name that starts with two underscores** (`__pycache__`).

`__pycache__` and `__pypackages__` hold what the interpreter produced, never source. Used by the base rule.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import IN_DUNDER_DIR

IN_DUNDER_DIR.is_valid(Path("pkg/__pycache__/app.cpython-312.py"))   # -> True
IN_DUNDER_DIR.is_valid(Path("__pycache__/app.py"))                   # -> True
IN_DUNDER_DIR.is_valid(Path("pkg/__init__.py"))                      # -> False    a FILE with underscores is not a folder
IN_DUNDER_DIR.is_valid(Path("pkg/_private/app.py"))                  # -> False    one underscore is an ordinary name
```

**Folders, not files.** The old base rule dropped every *file* whose name started with two underscores and lost
`__init__.py` and `__main__.py` that way. This rule looks only at the folders above a file.

<details>
<summary>🔍 Under the hood</summary>

```python
IN_DUNDER_DIR: Final[Rule] = AnyParentNameIs(StartsWith("__"))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `VCS_DIRS`

**The file lies inside a version-control folder** (`.git`, `.svn`, `.hg`, `.bzr`).

Part of the strict exclusion. The names are `IGNORE_VCS` of `simplibs-path`: version control is the same for every
language, so the library borrows the list instead of keeping its own.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import VCS_DIRS

VCS_DIRS.is_valid(Path(".git/hooks/pre-commit.py"))      # -> True
VCS_DIRS.is_valid(Path(".github/workflows/ci.py"))       # -> False   `.github` is not `.git`
VCS_DIRS.is_valid(Path("src/app.py"))                    # -> False
```

**What changed from the old code.** The old list also held `node_modules` and `tmp`. Neither is version control:
`node_modules` belongs to the JavaScript add-on and `tmp` is dropped.

<details>
<summary>🔍 Under the hood</summary>

```python
VCS_DIRS: Final[Rule] = AnyParentNameIs(IsIn(IGNORE_VCS))
```

`IsIn` compares a folder name as a whole.

</details>

[▲ Back to top](#-table-of-contents)

---

### `VENV_DIRS`

**The file lies inside a Python virtual environment folder.**

The names are [`PYTHON_VENV_DIR_NAMES`](README_EXTRACTOR_PYTHON_CONSTANTS.md#python_venv_dir_names), including the known
limit: a folder called `env` that is something else is left out as well.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import VENV_DIRS

VENV_DIRS.is_valid(Path(".venv/lib/site.py"))            # -> True
VENV_DIRS.is_valid(Path("env/settings.py"))              # -> True     the known limit
VENV_DIRS.is_valid(Path("src/environment/app.py"))       # -> False    whole names only
```

<details>
<summary>🔍 Under the hood</summary>

```python
VENV_DIRS: Final[Rule] = AnyParentNameIs(IsIn(PYTHON_VENV_DIR_NAMES))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `OUTPUT_DIRS`

**The file lies inside a build-output folder.**

Build output repeats the source in another shape. The names are
[`PYTHON_OUTPUT_DIR_NAMES`](README_EXTRACTOR_PYTHON_CONSTANTS.md#python_output_dir_names).

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import OUTPUT_DIRS

OUTPUT_DIRS.is_valid(Path("build/lib/app.py"))           # -> True
OUTPUT_DIRS.is_valid(Path("dist/app.py"))                # -> True
OUTPUT_DIRS.is_valid(Path("src/distribution/app.py"))    # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
OUTPUT_DIRS: Final[Rule] = AnyParentNameIs(IsIn(PYTHON_OUTPUT_DIR_NAMES))
```

</details>

[▲ Back to top](#-table-of-contents)

---

## `python/` — the rules of a Python project

### `PYTHON_BASE`

**The default choice of Python files worth reading.**

`build_python_base()` with its defaults, built once. Every Python profile of this library uses it as `include`:
Python files, **with** `__init__.py` and `__main__.py`, without dot files and without anything inside a folder such as
`__pycache__`.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import PYTHON_BASE

PYTHON_BASE.is_valid(Path("src/app.py"))  # -> True
PYTHON_BASE.is_valid(Path("src/__init__.py"))  # -> True
PYTHON_BASE.is_valid(Path("src/__version__.py"))  # -> True     an ordinary module
PYTHON_BASE.is_valid(Path("src/.hidden.py"))  # -> False    a dot file
PYTHON_BASE.is_valid(Path("src/__pycache__/app.py"))  # -> False    the interpreter's own folder
PYTHON_BASE.is_valid(Path("../README.md"))  # -> False    not Python
PYTHON_BASE.is_valid(Path("stubs/app.pyi"))  # -> False    a stub only repeats signatures
```

**It does not look at tests, configuration or environments.** That is the job of
[`PYTHON_STRICT_EXCLUDE`](#python_strict_exclude), and a profile chooses whether to use it.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_BASE: Final[Rule] = build_python_base()
```

The constant has a file of its own, and the function a name that differs from it by more than the case — see
[`build_python_base`](#build_python_base).

</details>

[▲ Back to top](#-table-of-contents)

---

### `build_python_base`

**Builds the rule that picks the Python files worth reading.**

Python files, without dot files and without anything inside a folder such as `__pycache__`. Two switches decide the two
package files.

**Parameters:**

| Name           | Type   | Default | Description                                                              |
|----------------|--------|---------|--------------------------------------------------------------------------|
| `include_init` | `bool` | `True`  | Take `__init__.py`. Switch off to read only the modules. *(keyword-only)* |
| `include_main` | `bool` | `True`  | Take `__main__.py`. Switch off to leave the entry point out. *(keyword-only)* |

**Returns:** a `Rule` on the path relative to the source folder.

**Raises:** `ValidationError` — an option is not a `bool`.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import build_python_base

modules_only = build_python_base(include_init=False, include_main=False)

modules_only.is_valid(Path("pkg/app.py"))                # -> True
modules_only.is_valid(Path("pkg/__init__.py"))           # -> False
modules_only.is_valid(Path("pkg/__main__.py"))           # -> False

build_python_base(include_init=False).is_valid(Path("pkg/__main__.py"))   # -> True    each switch alone
build_python_base(include_main=False).is_valid(Path("pkg/__init__.py"))   # -> True
```

**What changed from the old `PythonBase`.** The old rule excluded every file whose name started with two underscores.
That took away `__init__.py`, which holds the public names of a package, and `__main__.py`, the entry point. Both are
taken by default now; the two switches bring the old behaviour back. Other names of that kind (`__version__.py`,
`__about__.py`) are ordinary modules and are taken as well.

**Why the name starts with `build_`.** The constant [`PYTHON_BASE`](#python_base) has a file of its own. On Windows and
macOS two files whose names differ only by case (`python_base.py`, `PYTHON_BASE.py`) are the same file, so the function
got a name that differs by more than the case.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def build_python_base(*, include_init: bool = True, include_main: bool = True) -> Rule:

    # 1. The core: Python files that are not hidden and not interpreter products
    rule = HasSuffix(*PYTHON_SUFFIXES) & ~DOT_NAME & ~IN_DUNDER_DIR

    # 2. The two package files, unless asked to leave them out
    if not include_init:
        rule = rule & ~INIT_NAME
    if not include_main:
        rule = rule & ~MAIN_NAME

    return rule
```

The rule is a plain combination of the atomic pieces: a suffix, **and not** a dot name, **and not** a folder of the
`__pycache__` kind. The two switches only add one more `& ~` each.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_TESTS`

**The file is a Python test:** by its name (`test_a.py`, `a_test.py`, `tests.py`, `conftest.py`) or by its folder
(`tests/`).

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import PYTHON_TESTS

# by the name
PYTHON_TESTS.is_valid(Path("src/test_app.py"))           # -> True
PYTHON_TESTS.is_valid(Path("src/app_test.py"))           # -> True
PYTHON_TESTS.is_valid(Path("src/app_tests.py"))          # -> True
PYTHON_TESTS.is_valid(Path("src/tests.py"))              # -> True
PYTHON_TESTS.is_valid(Path("conftest.py"))               # -> True

# by the folder
PYTHON_TESTS.is_valid(Path("tests/helpers.py"))          # -> True     a helper of the tests, whatever it is called

# not tests
PYTHON_TESTS.is_valid(Path("src/latest_data.py"))        # -> False
PYTHON_TESTS.is_valid(Path("src/contest.py"))            # -> False
PYTHON_TESTS.is_valid(Path("src/attest.py"))             # -> False
PYTHON_TESTS.is_valid(Path("src/testing.py"))            # -> False
```

**Why a pattern on the whole name.** The old rule asked whether the path *contained* `test` — and threw away
`latest_data.py`, `contest.py` and `attest.py`. The pattern is anchored at both ends: the name starts with `test_`, ends
with `_test` or `_tests`, or is exactly `test`, `tests` or `conftest`, followed by `.py`.

**Or anywhere inside a tests folder.** Every file in a folder called `tests` or `test` is at least a test helper.
`src/tests/helpers.py` counts, and so does `tests/unit/a.py` — the rule looks at **every** folder above the file.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_TESTS: Final[Rule] = (
    NameIs(Regex(r"^(test_.*|.*_tests?|tests?|conftest)\.py$"))
    | AnyParentNameIs(IsIn(PYTHON_TEST_DIR_NAMES))
)
```

The first half judges the name, the second half the folders above it; `|` makes a file a test if **either** is true.
The folder names are [`PYTHON_TEST_DIR_NAMES`](README_EXTRACTOR_PYTHON_CONSTANTS.md#python_test_dir_names).

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_CONFIG`

**The file is Python project configuration** (`setup.py`, `tox.ini`, `requirements.txt`, ...).

`setup.py` is Python source, but it describes packaging; for reading what the project does it is noise.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import PYTHON_CONFIG

PYTHON_CONFIG.is_valid(Path("setup.py"))  # -> True
PYTHON_CONFIG.is_valid(Path("../pyproject.toml"))  # -> True
PYTHON_CONFIG.is_valid(Path("pkg/setup.py"))  # -> True     only the NAME is judged, at any depth
PYTHON_CONFIG.is_valid(Path("Pipfile"))  # -> True
PYTHON_CONFIG.is_valid(Path("pipfile"))  # -> False    compared exactly
PYTHON_CONFIG.is_valid(Path("src/app.py"))  # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_CONFIG: Final[Rule] = NameIs(IsIn(PYTHON_CONFIG_NAMES))
```

The names are [`PYTHON_CONFIG_NAMES`](README_EXTRACTOR_PYTHON_CONSTANTS.md#python_config_names).

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_STRICT_EXCLUDE`

**Everything that is Python-looking but not the project's own logic:** tests, configuration, environments, build output
and version control.

The `exclude` of the profile `python/src-clean`. The old code had a strict filter like this, but no profile ever used
it — now one does.

**Kind:** `Rule` on a path.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_STRICT_EXCLUDE

PYTHON_STRICT_EXCLUDE.is_valid(Path("tests/test_app.py"))   # -> True
PYTHON_STRICT_EXCLUDE.is_valid(Path("setup.py"))            # -> True
PYTHON_STRICT_EXCLUDE.is_valid(Path(".venv/lib/site.py"))   # -> True
PYTHON_STRICT_EXCLUDE.is_valid(Path("build/lib/app.py"))    # -> True
PYTHON_STRICT_EXCLUDE.is_valid(Path("src/app.py"))          # -> False

# the whole selection of `python/src-clean` as one rule
own_logic = PYTHON_BASE & ~PYTHON_STRICT_EXCLUDE
own_logic.is_valid(Path("src/app.py"))                      # -> True
own_logic.is_valid(Path("src/test_app.py"))                 # -> False
```

**How it combines.** Used together with `PYTHON_BASE` as `include`: a file must be Python source **and** must not be any
of these. In a profile the two are given separately (`include=`, `exclude=`); a config you pass to one `extract` call can
only **narrow** them further.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_STRICT_EXCLUDE: Final[Rule] = PYTHON_TESTS | PYTHON_CONFIG | VENV_DIRS | OUTPUT_DIRS | VCS_DIRS
```

Five rules joined by `|`: a file that matches **any** of them is excluded.

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-file_rules--which-files-are-worth-reading)
