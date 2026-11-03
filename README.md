# 🐍 `simplibs-extractor-python`

[![PyPI](https://img.shields.io/pypi/v/simplibs-extractor-python)](https://pypi.org/project/simplibs-extractor-python/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-extractor-python/blob/main/LICENSE)
[![tests](https://github.com/simplibs/simplibs-extractor-python/actions/workflows/tests.yml/badge.svg)](https://github.com/simplibs/simplibs-extractor-python/actions)

**A Python project in one document — the code, with or without its paperwork.**

The Python add-on of [`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/). The extractor gathers the
text files of a folder into one document and knows **no language**; this library teaches it Python: which files are
worth reading, how to take **comments, docstrings, imports and decorators** out of a source, how to write an
**outline** of its classes and functions, and five ready **profiles** that put it together. Python is read with `ast`
and `tokenize`, never with a regex — so a `#` inside a string is left alone.

```bash
pip install simplibs-extractor-python
simplibs-extractor python src-clean my_project
```

```python
from simplibs.extractor_python import remove_python_comments, python_outline

remove_python_comments("x = 1  # note\ny = '# not a comment'\n")   # -> "x = 1\ny = '# not a comment'\n"
python_outline("class A:\n    def m(self, n: int = 1) -> str:\n        return ''\n")
# -> 'class A:\n    def m(self, n: int=1) -> str: ...\n'
```

> `pip install` is the whole installation: the library announces itself to the extractor through an entry point, so the
> profiles show up in `simplibs-extractor --list-systems` with nothing to import. The same steps are plain functions
> (`str -> str`) you can use without the extractor at all.

---

## 🧭 The Core Philosophy

Cleaning source code with a few regular expressions works until the first file where it does not: a `#` in a URL inside a
string, an `import` in a docstring, a docstring that was the only statement of a function, `import a; x = 1` on one line.
`simplibs-extractor-python` is built around those traps:

* **Python is read by Python.** The comments are found by `tokenize`, the docstrings, imports and decorators by `ast`.
  A `#` inside `"http://x/#anchor"` is not a comment, and `from` inside a string is not an import.
* **Cut by position, change nothing else.** A removal cuts exactly the characters of what it found; the rest of the file
  stays as it was written — quotes, spacing, line breaks. The step does not re-format, so the output can be compared with
  the original.
* **The tree stays.** For a source that parses, the syntax tree of the result equals the tree of the original **minus**
  what the step removes. A block that would be left empty gets a `pass`, a `;` that joined two statements goes with the
  one that was removed — the result is still Python.
* **One bad file never stops a run.** A file that cannot be read (an old Python 2 file, a half-written module) raises one
  card, the extractor marks **that file** `error` with the reason and goes on. For a profile where "not cleaned" is better
  than "not there", `on_error="keep"` gives the text back unchanged.
* **A name is a whole name.** A test is `test_a.py`, `a_test.py`, `tests.py`, `conftest.py` or anything in a folder called
  `tests` — not `latest_data.py`, `contest.py` or `attest.py`. A folder is `tests` or it is not.
* **A package is source.** `__init__.py` holds the public names of a package and `__main__.py` its entry point; both are
  taken by default. What the interpreter made (`__pycache__`) is not.
* **Rules judge the path inside the source.** A project that lies in a folder called `tests` is not dropped as "a test";
  the rules see only what is *inside* the source folder.
* **For reading, not for running.** A removal of decorators can change what a function *is*, a removal of imports leaves
  names without their origin. The profiles say so, and the output is built for a reader — a person or a model.
* **Functions first, actions on top.** Every step is a plain function; the action is a thin wrapper over the function of
  the same name, and the presets and profiles are built from the actions. The logic lives once.
* **Every error is a card.** An unreadable source is one structured card from
  [`simplibs-exception`](https://pypi.org/project/simplibs-exception/): what, why, how to fix.
* **Layers that only look left.** `annotations` ← `constants` ← `file_rules` ← `logic` ← `actions` ← `presets` ←
  `profiles` ← `plugin` — every layer imports only from those before it.

```python
remove_python_imports("print 'hello'\n")                 # -> raises: CODE_EXTRACTOR_PYTHON_SOURCE_INVALID — Python 2, the file cannot be read
remove_python_imports("print 'hello'\n", on_error="keep")   # -> "print 'hello'\n"   the text back, unchanged
```

---

## 📦 Installation

```bash
pip install simplibs-extractor-python
```

Requires Python 3.11+. The package brings [`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/) with it,
and the command `simplibs-extractor` is available at once. Runtime dependencies, all from the same family:
[`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/) (the profile, the registry),
[`simplibs-text`](https://pypi.org/project/simplibs-text/) (cutting the found ranges, the whitespace presets),
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/) (the steps as actions),
[`simplibs-path`](https://pypi.org/project/simplibs-path/) and [`simplibs-rules`](https://pypi.org/project/simplibs-rules/)
(the file rules), [`simplibs-validate`](https://pypi.org/project/simplibs-validate/) and
[`simplibs-exception`](https://pypi.org/project/simplibs-exception/) (the checks and the error card).

> **The running Python decides what is valid.** A source is read by the interpreter that runs the step: a file with syntax
> newer than that interpreter (`def f[T](x: T)` is Python 3.12+) is a file it cannot read — an `error` line in the
> report, or an unchanged file with `on_error="keep"`.

---

## 🚀 Quick Start in 60 Seconds

### Level 1: The command line

```bash
simplibs-extractor python src-clean my_project                     # the project's own logic, cleaned -> my_project/python_src_clean.md
simplibs-extractor python code-no-imports my_project               # the logic only
simplibs-extractor python outline my_project                       # signatures without bodies — the smallest overview
simplibs-extractor python code-clean,data-all my_project           # two profiles -> two files, one run
simplibs-extractor python data-all my_project --dry-run            # plan and report, write nothing
simplibs-extractor --list-profiles python                          # the five profiles
```

Which one? `data-all` gives the files as they are, `code-clean` takes the prose away (comments, docstrings), `src-clean`
does the same and leaves out tests, configuration, environments and build folders, `code-no-imports` takes also the
imports and decorators away, `outline` keeps only what a project offers.

### Level 2: The steps as functions

```python
from simplibs.extractor_python import (
    remove_python_comments, remove_python_docstrings, remove_python_imports, remove_python_decorators, python_outline,
)

remove_python_comments("x = 1  # note\n# alone\ny = '# not a comment'\n")      # -> "x = 1\ny = '# not a comment'\n"
remove_python_docstrings('class A:\n    """doc"""\n\ndef f():\n    """doc"""\n')
# -> 'class A:\n    pass\n\ndef f():\n    pass\n'                              a body needs a statement
remove_python_imports("import a; x = 1\ny = 2; import b\n")                    # -> 'x = 1\ny = 2\n'
remove_python_decorators("@app.route('/')\n@cache(60)\ndef index():\n    pass\n")   # -> 'def index():\n    pass\n'
python_outline("@dec\nclass A(B):\n    def m(self, a: int = 1) -> str:\n        return ''\n")
# -> '@dec\nclass A(B):\n    def m(self, a: int=1) -> str: ...\n'
```

### Level 3: Actions and ready-made chains

```python
from simplibs.extractor_python.actions import PythonOutline, RemovePythonComments, RemovePythonImports
from simplibs.extractor_python.presets import PYTHON_CLEAN, PYTHON_NO_IMPORTS

steps = RemovePythonComments() >> RemovePythonImports()
steps("import os\n\n# c\nx = 1  # n\n")                  # -> '\nx = 1\n'

PYTHON_CLEAN("import os\n# c\nx = 1  # n\n")             # -> 'import os\nx = 1\n'
PYTHON_NO_IMPORTS('import os\n\n@cache(60)\ndef f():\n    """Doc."""\n    return 1  # one\n')
# -> 'def f():\n    return 1\n'

PythonOutline(docstrings=False)("def f(): '''d'''\n")    # -> 'def f(): ...\n'
```

### Level 4: Your own profile from the parts

File rules combine with `&`, `|` and `~`; the steps chain with `>>`; a registered profile is a name for both.

```python
from simplibs.extractor import Profile, by_suffix, extract, register_profile
from simplibs.extractor_python.constants import PYTHON_SUFFIXES
from simplibs.extractor_python.file_rules import PYTHON_BASE, PYTHON_TESTS
from simplibs.extractor_python.presets import PYTHON_CLEAN

register_profile(Profile(
    system="python", name="tests-clean",
    description="The tests, without comments and docstrings",
    include=PYTHON_BASE & PYTHON_TESTS,                  # Python files that are tests
    steps=by_suffix(PYTHON_CLEAN, PYTHON_SUFFIXES),
    output_name="python_tests_clean.md",
))

extract(source="my_project", profile="python/tests-clean")
```

A changed copy of a profile of this library is one `dataclasses.replace` away:

```python
from dataclasses import replace
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN

mine = replace(PYTHON_SRC_CLEAN, name="mine", output_name="mine.md")
```

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/extractor_python/
├── annotations/          ◄── OnError
├── constants/            ◄── PYTHON_SUFFIXES, PYTHON_CONFIG_NAMES, PYTHON_TEST_DIR_NAMES, PYTHON_VENV_DIR_NAMES, PYTHON_OUTPUT_DIR_NAMES
├── file_rules/           ◄── Rules on the path inside the source (domain folder)
│   ├── atomic/           ◄── DOT_NAME, INIT_NAME, MAIN_NAME, IN_DUNDER_DIR, VCS_DIRS, VENV_DIRS, OUTPUT_DIRS
│   └── python/           ◄── PYTHON_BASE, build_python_base, PYTHON_TESTS, PYTHON_CONFIG, PYTHON_STRICT_EXCLUDE
├── logic/                ◄── The steps: plain functions that read Python with ast and tokenize
│   ├── python_comment_spans.py  remove_python_comments.py  remove_python_docstrings.py  ...
│   └── _helpers/  _validations/                          ◄── Private: offsets, the parser guard, statement cutting, the card
├── actions/              ◄── The steps as Action classes (domain folder)
├── presets/              ◄── Ready-made chains: PYTHON_CLEAN, PYTHON_NO_IMPORTS (domain folder)
├── profiles/             ◄── The five Profile objects and PYTHON_PROFILES (domain folder)
├── plugin/               ◄── register_all: the target of the entry point
└── py.typed
```

Folders named `_helpers/` and `_validations/` are private: they hold the small tools of the steps and the function that
raises the library's one error card.

The package root exports **the steps**, `register_all` and `OnError`. The four domain folders have their own `__all__` and
are imported through their domain — a function and an action are different kinds of thing and should stay visibly
different at the import line:

```python
from simplibs.extractor_python import remove_python_comments, python_outline, OnError          # the steps and the type
from simplibs.extractor_python.actions import RemovePythonComments                              # the steps as actions
from simplibs.extractor_python.file_rules import PYTHON_BASE, build_python_base                 # the rules
from simplibs.extractor_python.presets import PYTHON_CLEAN                                      # ready-made chains
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN                                 # the profiles as objects
```

The ranges the steps find are `simplibs.text.Span`; the type is taken from `simplibs-text`, not defined here.

---

## 🔧 `logic/` — The steps that read Python

Plain functions: a Python source as a text in, a text out (one of them gives the positions of the comments). All take the
option `on_error`.

| Function                   | Description / Parameters                                                                                              |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `python_comment_spans`     | Finds the comments with the tokenizer; returns a `Span` for each, from the blanks in front to the end (`text`, keyword-only: `on_error="raise"`). |
| `remove_python_comments`   | Removes every comment; a line that held only a comment disappears (`text`, keyword-only: `on_error="raise"`).          |
| `remove_python_docstrings` | Removes the docstrings of the module, classes and functions; an emptied body gets `pass` (`text`, keyword-only: `on_error="raise"`). |
| `remove_python_imports`    | Removes the imports at any depth; an emptied body gets `pass`, `import a; x = 1` keeps `x = 1` (`text`, keyword-only: `on_error="raise"`). |
| `remove_python_decorators` | Removes the decorators of every class and function, from the `@` (`text`, keyword-only: `on_error="raise"`).           |
| `python_outline`           | Writes classes and functions as signatures without bodies — valid Python again (`text`, keyword-only: `docstrings=True`, `on_error="raise"`). |

➡️ [README_EXTRACTOR_PYTHON_LOGIC](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/logic/README_EXTRACTOR_PYTHON_LOGIC.md)

---

## 🔗 `actions/` — The steps as pipeline actions

Every step except `python_comment_spans` is also an `Action` of
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/): configured once, called with the **text** as its main
input, chainable with `>>`. The options of the function are the options of the action:
`RemovePythonImports(on_error="keep")`.

| Action                   | Over                       | Description                                                  |
|--------------------------|----------------------------|--------------------------------------------------------------|
| `RemovePythonComments`   | `remove_python_comments`   | Takes the comments out of the text flowing in.               |
| `RemovePythonDocstrings` | `remove_python_docstrings` | Takes the docstrings out.                                    |
| `RemovePythonImports`    | `remove_python_imports`    | Takes the import statements out.                             |
| `RemovePythonDecorators` | `remove_python_decorators` | Takes the decorators out.                                    |
| `PythonOutline`          | `python_outline`           | Turns the text into signatures without bodies.               |

➡️ [README_EXTRACTOR_PYTHON_ACTIONS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_ACTIONS.md)

---

## 🧩 `presets/` — Ready-made chains

Chains of actions, built once, that the profiles use.

| Preset              | Chain                                                                                                  |
|---------------------|--------------------------------------------------------------------------------------------------------|
| `PYTHON_CLEAN`      | `RemovePythonComments() >> RemovePythonDocstrings() >> CLEANUP_WHITESPACE` — the imports stay.        |
| `PYTHON_NO_IMPORTS` | `RemovePythonComments() >> RemovePythonDocstrings() >> RemovePythonImports() >> RemovePythonDecorators() >> COMPACT` — the logic only. |

`CLEANUP_WHITESPACE` squeezes blank runs to one line, `COMPACT` removes every blank line (also inside a multi-line string).

➡️ [README_EXTRACTOR_PYTHON_PRESETS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PRESETS.md)

---

## 📋 `profiles/` — The five profiles

Registered in the system `python`; also importable as `Profile` objects.

| Profile                  | Output                      | Description                                                                                 |
|--------------------------|-----------------------------|---------------------------------------------------------------------------------------------|
| `python/code-clean`      | `python_code_clean.md`      | Python without comments, docstrings and extra blank lines (imports stay).                   |
| `python/code-no-imports` | `python_code_no_imports.md` | Pure logic: no imports, decorators, comments, docstrings or blank lines.                    |
| `python/data-all`        | `python_data_all.md`        | Every relevant `.py` file, as it is.                                                        |
| `python/outline`         | `python_outline.md`         | Overview of classes and functions: signatures without bodies.                               |
| `python/src-clean`       | `python_src_clean.md`       | Like `code-clean`, without tests, configuration, environments and build folders.            |

`PYTHON_PROFILES` is the tuple of all five, in the order the listings show them.

➡️ [README_EXTRACTOR_PYTHON_PROFILES](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PROFILES.md)

---

## 📐 `file_rules/` — Which files are worth reading

Rules on the path **inside** the source folder: `Rule` objects of
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/), composable with `&`, `|` and `~`.

| Rule / function         | Description / Parameters                                                                                       |
|-------------------------|----------------------------------------------------------------------------------------------------------------|
| `PYTHON_BASE`           | The default choice: Python files, with `__init__.py` and `__main__.py`, without dot files and `__pycache__`.    |
| `build_python_base`     | Builds that rule with switches (keyword-only: `include_init=True`, `include_main=True`).                         |
| `PYTHON_TESTS`          | A test by its whole name (`test_a.py`, `a_test.py`, `tests.py`, `conftest.py`) or by its folder (`tests/`).     |
| `PYTHON_CONFIG`         | Project configuration: `setup.py`, `pyproject.toml`, `tox.ini`, `requirements.txt`, ...                         |
| `PYTHON_STRICT_EXCLUDE` | Tests, configuration, environments, build output and version control together.                                  |

The atomic pieces they are made of: `DOT_NAME`, `INIT_NAME`, `MAIN_NAME`, `IN_DUNDER_DIR`, `VCS_DIRS`, `VENV_DIRS`,
`OUTPUT_DIRS`.

➡️ [README_EXTRACTOR_PYTHON_FILE_RULES](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_FILE_RULES.md)

---

## 🔖 `annotations/` and `constants/`

| Name                      | Kind     | Description                                                                         |
|---------------------------|----------|-------------------------------------------------------------------------------------|
| `OnError`                 | Literal  | `"raise"` or `"keep"`: what a step does with a source it cannot read. Exported from the package root. |
| `PYTHON_SUFFIXES`         | Constant | `(".py",)` — the suffixes of Python source.                                         |
| `PYTHON_CONFIG_NAMES`     | Constant | File names of project configuration.                                                |
| `PYTHON_TEST_DIR_NAMES`   | Constant | `("tests", "test")`.                                                                |
| `PYTHON_VENV_DIR_NAMES`   | Constant | `("venv", ".venv", "env", "virtualenv")`.                                           |
| `PYTHON_OUTPUT_DIR_NAMES` | Constant | `("build", "dist", "out")`.                                                         |

➡️ [README_EXTRACTOR_PYTHON_ANNOTATIONS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_ANNOTATIONS.md) · [README_EXTRACTOR_PYTHON_CONSTANTS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_CONSTANTS.md)

---

## 🔌 `plugin/` — The meeting point with the extractor

| Function       | Description / Parameters                                                                                                  |
|----------------|---------------------------------------------------------------------------------------------------------------------------|
| `register_all` | Registers the five profiles in the extractor's registry and returns their keys; the target of the entry point `simplibs.extractor.plugins` (keyword-only: `replace_existing=True`). |

The entry point lives in this library's `pyproject.toml`; the extractor's `load_plugins()` finds it, so nothing is
imported by name. From Python, call `load_plugins()` of the extractor once before a profile is looked up.

➡️ [README_EXTRACTOR_PYTHON_PLUGIN](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PLUGIN.md)

---

## ⚠️ Exceptions

The library defines no exceptions of its own. A source that cannot be read is one structured
[`simplibs.exception`](https://pypi.org/project/simplibs-exception/) card; a caller that wants "any error of the family"
catches `SimpleError`.

| Error name                             | Class        | Wraps        | Raised when                                                                                      |
|----------------------------------------|--------------|--------------|--------------------------------------------------------------------------------------------------|
| `CODE_EXTRACTOR_PYTHON_SOURCE_INVALID` | `ParamError` | `ValueError` | A step gets a text that cannot be read as Python — a syntax error, a bad indentation, an unterminated string, a null character, line endings other than `\n` — and `on_error` is `"raise"`. |

What is an exception and what is not:

| Situation                                                                   | How it is reported                                                       |
|-----------------------------------------------------------------------------|--------------------------------------------------------------------------|
| A step called directly on **an unreadable source**                          | the card above, **raised** (or the text back with `on_error="keep"`)     |
| The same inside an **extraction**                                           | **not raised**: that file is `error` in the result, the run continues    |
| A wrong **type** of an argument (`text=5`, `on_error="ignore"`)             | a `ValidationError` from `simplibs-validate`                             |
| A profile key that is taken, with `register_all(replace_existing=False)`    | the card of the extractor's registry (`EXTRACTOR_PROFILE_EXISTS`)        |

---

## 📚 Documentation

The detailed references — every function, rule and profile with its parameters, return value, raised errors, an example
and a look under the hood:

| Reference | What it describes |
|-----------|-------------------|
| [LOGIC](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/logic/README_EXTRACTOR_PYTHON_LOGIC.md) | the six steps: comments, docstrings, imports, decorators, the outline |
| [ACTIONS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_ACTIONS.md) | the steps as pipeline actions |
| [PRESETS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PRESETS.md) | `PYTHON_CLEAN`, `PYTHON_NO_IMPORTS` |
| [PROFILES](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PROFILES.md) | the five profiles, one file through each, a profile of your own |
| [FILE_RULES](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_FILE_RULES.md) | which files are worth reading: the atomic pieces and the rules of a Python project |
| [ANNOTATIONS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_ANNOTATIONS.md) | `OnError` |
| [CONSTANTS](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_CONSTANTS.md) | the fixed values: suffixes and folder names |
| [PLUGIN](https://github.com/simplibs/simplibs-extractor-python/blob/main/docs/README_EXTRACTOR_PYTHON_PLUGIN.md) | `register_all` and how the extractor finds this add-on |

---

## 🔗 Related libraries

* **[`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/)** — the extractor this library is an add-on of: the six phases, the profiles and the command.
* **[`simplibs-text`](https://pypi.org/project/simplibs-text/)** — `remove_spans` cuts the ranges the steps find; `CLEANUP_WHITESPACE` and `COMPACT` close the presets.
* **[`simplibs-actions`](https://pypi.org/project/simplibs-actions/)** — the `Action` the steps are wrapped in.
* **[`simplibs-path`](https://pypi.org/project/simplibs-path/)** — the path rules (`HasSuffix`, `NameIs`, `AnyParentNameIs`) and `IGNORE_VCS`.
* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** — the `Rule` object and its building blocks (`IsIn`, `Equals`, `StartsWith`, `Regex`).
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** and **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the checks of every signature and the error card.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---
