# 🔢 `constants` — Fixed Values

The `constants` package holds the **names** the file rules and profiles are built from: which suffix is Python, which
folders hold tests, environments and build output, which files configure a project. Every value is a **tuple of plain
strings** (`Final`), so a rule is built from them in `file_rules` and nothing else needs to know the lists.

```python
from simplibs.extractor_python.constants import PYTHON_SUFFIXES, PYTHON_TEST_DIR_NAMES
```

The constants are importable from `simplibs.extractor_python.constants`; the package root does not export them.

A few rules of the lists:

* **Names are compared as a whole.** A folder is `tests` or it is not; `contest` and `latest` are not tests. A file is
  `Pipfile` — with its capital letter, as the tool that owns it writes it — or it is not.
* **The library keeps its own lists.** What counts as build output differs from language to language, so each add-on
  decides it for its own language instead of borrowing a list.
* **Version control is not here.** Its folder names are `IGNORE_VCS` of
  [`simplibs-path`](https://pypi.org/project/simplibs-path/), the same for every language.

---

## 🧭 Table of Contents

* [`PYTHON_SUFFIXES`](#python_suffixes)
* [`PYTHON_CONFIG_NAMES`](#python_config_names)
* [`PYTHON_TEST_DIR_NAMES`](#python_test_dir_names)
* [`PYTHON_VENV_DIR_NAMES`](#python_venv_dir_names)
* [`PYTHON_OUTPUT_DIR_NAMES`](#python_output_dir_names)

[⬅️ Back to main README](../README.md#-annotations-and-constants)

---

### `PYTHON_SUFFIXES`

**The suffixes of Python source files.**

**Value:** `(".py",)`

**Used by:** `build_python_base` (the base rule) and every profile that has steps (`by_suffix(..., PYTHON_SUFFIXES)`).

**Example usage:**

```python
from simplibs.extractor_python.constants import PYTHON_SUFFIXES

PYTHON_SUFFIXES                                          # -> ('.py',)
".py" in PYTHON_SUFFIXES                                 # -> True
".pyi" in PYTHON_SUFFIXES                                # -> False
```

**Only `.py`.** A stub file (`.pyi`) only repeats the signatures of a module that is in the output anyway, and a
Windows script (`.pyw`) is not source to read.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_SUFFIXES: Final[tuple[str, ...]] = (".py",)
```

A tuple even with one item: the rule is `HasSuffix(*PYTHON_SUFFIXES)`, so adding a suffix is a change of one line here
and nowhere else.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_CONFIG_NAMES`

**File names of Python project configuration.**

**Value:** `("setup.py", "setup.cfg", "pyproject.toml", "Pipfile", "Pipfile.lock", "requirements.txt", "tox.ini", "pytest.ini")`

**Used by:** [`PYTHON_CONFIG`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_config).

**Example usage:**

```python
from simplibs.extractor_python.constants import PYTHON_CONFIG_NAMES

"setup.py" in PYTHON_CONFIG_NAMES                        # -> True
"Pipfile" in PYTHON_CONFIG_NAMES                         # -> True
"pipfile" in PYTHON_CONFIG_NAMES                         # -> False    compared exactly
```

**Packaging, not logic.** These files describe how the project is built and tested — not what it does. Most of them are
not `.py` files and never get as far as the base rule; the list matters for `setup.py`, which **is** Python source and,
for a reader who wants the logic, is noise.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_CONFIG_NAMES: Final[tuple[str, ...]] = (
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "requirements.txt",
    "tox.ini",
    "pytest.ini",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_TEST_DIR_NAMES`

**Names of folders that hold Python tests.**

**Value:** `("tests", "test")`

**Used by:** [`PYTHON_TESTS`](README_EXTRACTOR_PYTHON_FILE_RULES.md#python_tests): every file in a folder with one of
these names is a test, whatever the file is called.

**Example usage:**

```python
from simplibs.extractor_python.constants import PYTHON_TEST_DIR_NAMES

"tests" in PYTHON_TEST_DIR_NAMES                         # -> True
"contest" in PYTHON_TEST_DIR_NAMES                       # -> False    whole names only
"latest" in PYTHON_TEST_DIR_NAMES                        # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_TEST_DIR_NAMES: Final[tuple[str, ...]] = ("tests", "test")
```

The rule that uses it is `AnyParentNameIs(IsIn(PYTHON_TEST_DIR_NAMES))`: `IsIn` compares a folder name as a whole,
which is the whole reason `contest/` is safe.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_VENV_DIR_NAMES`

**Names under which a Python virtual environment usually lives.**

**Value:** `("venv", ".venv", "env", "virtualenv")`

**Used by:** [`VENV_DIRS`](README_EXTRACTOR_PYTHON_FILE_RULES.md#venv_dirs). A virtual environment holds thousands of
files that are not the project.

**Example usage:**

```python
from simplibs.extractor_python.constants import PYTHON_VENV_DIR_NAMES

".venv" in PYTHON_VENV_DIR_NAMES                         # -> True
"env" in PYTHON_VENV_DIR_NAMES                           # -> True
```

**A known limit.** A folder called `env` that is something else — a settings package, say — is left out by the strict
rules. The **base** rule does not look at these names, so only the profile `python/src-clean` is affected; if your
project has such a folder, use `python/code-clean` or build your own `exclude` from the atomic rules.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_VENV_DIR_NAMES: Final[tuple[str, ...]] = ("venv", ".venv", "env", "virtualenv")
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_OUTPUT_DIR_NAMES`

**Names of folders that hold generated build output of a Python project.**

**Value:** `("build", "dist", "out")`

**Used by:** [`OUTPUT_DIRS`](README_EXTRACTOR_PYTHON_FILE_RULES.md#output_dirs). Build output repeats the source in
another shape; reading it twice only costs tokens.

**Example usage:**

```python
from simplibs.extractor_python.constants import PYTHON_OUTPUT_DIR_NAMES

"dist" in PYTHON_OUTPUT_DIR_NAMES                        # -> True
"distribution" in PYTHON_OUTPUT_DIR_NAMES                # -> False
```

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_OUTPUT_DIR_NAMES: Final[tuple[str, ...]] = ("build", "dist", "out")
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-annotations-and-constants)
