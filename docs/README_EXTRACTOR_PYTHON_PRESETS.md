# 🧩 `presets` — Ready-Made Pipeline Steps

The `presets` package holds **chains of actions, built once**: the two cleanings that the profiles use, as objects you
can drop into a pipeline or give to a profile as `steps`.

```python
from simplibs.extractor_python.presets import PYTHON_CLEAN, PYTHON_NO_IMPORTS
```

A preset is a pipeline step: you **call** it with a text, or you chain it with `>>`.

```python
from simplibs.extractor_python.presets import PYTHON_CLEAN

PYTHON_CLEAN("import os\n# c\nx = 1  # n\n")             # -> 'import os\nx = 1\n'
```

The presets are **not** exported from the package root — they are a domain of their own, with their own `__all__`,
imported through `simplibs.extractor_python.presets`. They stand to the right of [`actions`](README_EXTRACTOR_PYTHON_ACTIONS.md)
(a preset is built **from actions**) and to the left of [`profiles`](README_EXTRACTOR_PYTHON_PROFILES.md) (which use them).

## The two presets

| Preset              | Chain                                                                                                      | Used by                                      |
|---------------------|------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| `PYTHON_CLEAN`      | `RemovePythonComments() >> RemovePythonDocstrings() >> CLEANUP_WHITESPACE`                                 | `python/code-clean`, `python/src-clean`      |
| `PYTHON_NO_IMPORTS` | `RemovePythonComments() >> RemovePythonDocstrings() >> RemovePythonImports() >> RemovePythonDecorators() >> COMPACT` | `python/code-no-imports`            |

`CLEANUP_WHITESPACE` and `COMPACT` are presets of [`simplibs-text`](https://pypi.org/project/simplibs-text/).

## The same source, two presets

```python
source = '''import os
# the limit
LIMIT = 10  # max


@cache(60)
def load(name):
    """Read one file."""
    return name  # as it is
'''
```

`PYTHON_CLEAN(source)`:

```python
import os
LIMIT = 10

@cache(60)
def load(name):
    return name
```

`PYTHON_NO_IMPORTS(source)`:

```python
LIMIT = 10
def load(name):
    return name
```

## A note on the order

Comments first, then docstrings: both find their targets in the original structure. Whitespace comes **last**, to tidy
the holes the first steps left — the usual "last pass" of a pipeline. In `PYTHON_NO_IMPORTS` the imports and decorators
stand between them; comments are already gone then, so a `# note` after a decorator is not left behind.

## A note on tidy and compact

The two presets end differently, on purpose:

* **`CLEANUP_WHITESPACE`** squeezes every run of blank lines to **one**; it does not remove them. Code stays in
  paragraphs a person can read.
* **`COMPACT`** removes **every** blank line — also those inside a multi-line string. This is the shortest form, meant
  for a reader (or a model) that needs the code and not its layout.

```python
text = "def f():\n    x = '''a\n\nb'''\n    return x\n"   # a blank line inside a string

PYTHON_CLEAN(text)                                       # -> "def f():\n    x = '''a\n\nb'''\n    return x\n"    the string is intact
PYTHON_NO_IMPORTS(text)                                  # -> "def f():\n    x = '''a\nb'''\n    return x\n"      the blank line is gone
```

If a blank line **in a string** matters, use `PYTHON_CLEAN` or build a chain of your own that ends with
`CLEANUP_WHITESPACE`.

## A note on sharing one object

A preset is created **once**, at import, and used wherever it is needed. That is safe because an action holds only its
options and no state between calls, so the same object can serve any number of pipelines and profiles. Each is declared
`Final`, so a type checker stops an accidental reassignment.

---

## 🧭 Table of Contents

* [`PYTHON_CLEAN`](#python_clean)
* [`PYTHON_NO_IMPORTS`](#python_no_imports)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-presets--ready-made-chains)

---

### `PYTHON_CLEAN`

**Python without comments and docstrings, whitespace tidied — the imports stay.**

The everyday clean read: the steps of `python/code-clean` and `python/src-clean` as one object.

**Main input:** the text (`str`). **Returns:** `str`.

**Example usage:**

```python
from simplibs.extractor_python.presets import PYTHON_CLEAN
from simplibs.extractor_python.actions import RemovePythonDecorators

PYTHON_CLEAN("import os\n# c\n\n\n\nx = 1  # n\n")        # -> 'import os\n\nx = 1\n'     the blank run is squeezed to one line

# the usual way to extend it: one more step in front of the tidy-up
(PYTHON_CLEAN >> RemovePythonDecorators())("@dec\ndef f(): ...\n")     # -> 'def f(): ...\n'
```

**Safe to run twice.** A text that was cleaned is not changed by a second pass — each step finds nothing.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_CLEAN: Final = (
    RemovePythonComments()
    >> RemovePythonDocstrings()
    >> CLEANUP_WHITESPACE
)
```

A file that is not valid Python makes a step raise; the extractor marks that file `error` and goes on with the others.

</details>

[▲ Back to top](#-table-of-contents)

---

### `PYTHON_NO_IMPORTS`

**Python reduced to its logic:** no comments, docstrings, imports or decorators, and no blank lines.

The steps of `python/code-no-imports`: what the code does, not what it is wired to.

**Main input:** the text (`str`). **Returns:** `str`.

**Example usage:**

```python
from simplibs.extractor_python.presets import PYTHON_NO_IMPORTS

PYTHON_NO_IMPORTS('import os\n\n@cache(60)\ndef f():\n    """Doc."""\n    return 1  # one\n')
# -> 'def f():\n    return 1\n'

PYTHON_NO_IMPORTS("class A:\n    '''d'''\n    import x\n")      # -> 'class A:\n    pass\n'    two steps empty one block, one `pass`
```

**Compact, not tidy.** See [the note above](#a-note-on-tidy-and-compact): `COMPACT` removes every blank line, also inside
a multi-line string.

<details>
<summary>🔍 Under the hood</summary>

```python
PYTHON_NO_IMPORTS: Final = (
    RemovePythonComments()
    >> RemovePythonDocstrings()
    >> RemovePythonImports()
    >> RemovePythonDecorators()
    >> COMPACT
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

This package raises **no cards of its own** and takes no options: a preset accepts any text. A text that is not Python
raises the card of the first step, `CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`; an argument that is not a `str` is a
`ValidationError` from the action that receives it.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-presets--ready-made-chains)
