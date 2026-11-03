# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-11-01

The first release: the Python add-on of [`simplibs-extractor`](https://pypi.org/project/simplibs-extractor/).
It carries over what the old code extractor knew about Python and rebuilds it on `ast` and `tokenize`.

### ✨ Added

#### Steps — plain functions, text in, text out

* `python_comment_spans(text, *, on_error="raise")` — finds the comments with the tokenizer and returns them as `Span`s (from the blanks in front of a comment to its end); a `#` inside a string is never a comment
* `remove_python_comments(text, *, on_error="raise")` — removes every comment; a line that held only a comment disappears, `x = 1  # note` becomes `x = 1`
* `remove_python_docstrings(text, *, on_error="raise")` — removes the docstrings of the module, its classes and its functions; a body left empty gets a `pass`
* `remove_python_imports(text, *, on_error="raise")` — removes the imports at any depth (`try`, `if TYPE_CHECKING`, inside functions); a body left empty gets a `pass`, `import a; x = 1` keeps `x = 1`
* `remove_python_decorators(text, *, on_error="raise")` — removes the decorators of every class and function, from the `@` to the end of the expression (`@(lambda f: f)` included)
* `python_outline(text, *, docstrings=True, on_error="raise")` — writes classes and functions as signatures without bodies, valid Python again; the first line of a docstring becomes a trailing comment

#### Actions — the steps as links of a pipeline

* `RemovePythonComments`, `RemovePythonDocstrings`, `RemovePythonImports`, `RemovePythonDecorators`, `PythonOutline` — one `Action` over each step, made with `create_action`; the options of the function are the options of the action. Imported from `simplibs.extractor_python.actions`

#### Presets — ready-made chains

* `PYTHON_CLEAN` — comments and docstrings out, whitespace tidied; the imports stay
* `PYTHON_NO_IMPORTS` — comments, docstrings, imports and decorators out, no blank lines; the logic and nothing else

#### Profiles — registered in the system `python`

* `python/code-clean` — `python_code_clean.md`
* `python/code-no-imports` — `python_code_no_imports.md`
* `python/data-all` — `python_data_all.md`, every relevant file as it is
* `python/outline` — `python_outline.md`, new: what a project offers, in a fraction of the size
* `python/src-clean` — `python_src_clean.md`, with the strict exclusion (the old strict filter, which no profile ever used, is a profile now)
* `PYTHON_PROFILES` — the five profile objects in the order the listings show them
* Imported from `simplibs.extractor_python.profiles`

#### File rules — judge the path inside the source

* `PYTHON_BASE`, `build_python_base(*, include_init=True, include_main=True)` — Python files that are not hidden and not in a folder such as `__pycache__`
* `PYTHON_TESTS` — a test by its whole name (`test_a.py`, `a_test.py`, `tests.py`, `conftest.py`) or by its folder (`tests/`, `test/`)
* `PYTHON_CONFIG`, `PYTHON_STRICT_EXCLUDE` — project configuration; tests, configuration, environments, build output and version control together
* Atomic pieces: `DOT_NAME`, `INIT_NAME`, `MAIN_NAME`, `IN_DUNDER_DIR`, `VCS_DIRS`, `VENV_DIRS`, `OUTPUT_DIRS`
* Imported from `simplibs.extractor_python.file_rules`

#### Constants, annotations and the add-on

* `PYTHON_SUFFIXES`, `PYTHON_CONFIG_NAMES`, `PYTHON_TEST_DIR_NAMES`, `PYTHON_VENV_DIR_NAMES`, `PYTHON_OUTPUT_DIR_NAMES` — the fixed values the rules are built from
* `OnError` — `Literal["raise", "keep"]`: what a step does with a source it cannot read
* `register_all(*, replace_existing=True)` — registers the five profiles; the target of the entry point `simplibs.extractor.plugins`, so `pip install` is the whole installation
* The card `CODE_EXTRACTOR_PYTHON_SOURCE_INVALID` (a `ParamError` wrapping `ValueError`) for a text that cannot be read as Python

#### Exceptions

* The library defines no exceptions of its own; a source that cannot be read raises the card above, which names the reason, the line and the ways out (leave the file out, normalize the line endings, or pass `on_error="keep"`)
* With `on_error="keep"` a step returns the text unchanged instead of raising
* A text with `\r` line endings is refused with the same card, because the cuts are counted on `\n`
* The function that raises the card is private: it lives in `logic/_validations/` next to the code that uses it

#### Typing

* `py.typed` marker — the package ships its type information

#### Package Layout

* `simplibs.extractor_python` exports the six steps, `OnError` and `register_all`; the actions, presets, profiles and file rules are imported from their own folders (`actions`, `presets`, `profiles`, `file_rules`), each of which declares its own `__all__`
* Layers that only look left: `annotations` ← `constants` ← `file_rules` ← `logic` ← `actions` ← `presets` ← `profiles` ← `plugin`
* The add-on uses `simplibs.extractor` only through its public names (`Profile`, `register_profile`, `by_suffix`)
* Importing the package registers nothing; the extractor calls `register_all` through the entry point

#### Dependencies

* `simplibs-extractor` — `Profile`, `register_profile`, `by_suffix`
* `simplibs-text` — `remove_spans`, `Span`, `CLEANUP_WHITESPACE` and `COMPACT`
* `simplibs-actions` — `create_action`: the steps as pipeline actions
* `simplibs-path` — `IGNORE_VCS` and the path rules (`HasSuffix`, `NameIs`, `AnyParentNameIs`)
* `simplibs-rules` — `Rule`, `IsIn`, `Equals`, `StartsWith` and `Regex`
* `simplibs-validate` — `@validate_call` on the public functions
* `simplibs-exception` — the card of the unreadable source (`ParamError`)

### 🔄 Changed from the old code extractor

* **`__init__.py` and `__main__.py` are source.** The old base rule dropped every file whose name started with two underscores, which took away the public names of a package and its entry point. Both are taken now; `build_python_base(include_init=False, include_main=False)` brings the old behaviour back
* **A test is recognised by its whole name.** The old rule asked whether the path *contained* `test` and threw away `latest_data.py`, `contest.py` and `attest.py`
* **Version control is `IGNORE_VCS` of `simplibs-path`.** The old list also held `node_modules` (a thing of the JavaScript add-on) and `tmp` (dropped)
* **Comments, docstrings, imports and decorators are found by the parser,** not by a regex: a `#` or an `import` inside a string is left alone

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)
