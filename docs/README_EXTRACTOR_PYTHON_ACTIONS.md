# 🔗 `actions` — The Steps as Pipeline Actions

Every step of [`logic`](logic/README_EXTRACTOR_PYTHON_LOGIC.md) is also an `Action` of
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/): configured once, called with the **text** as its main
input, and chainable with `>>`. That is the form a profile needs, because the `steps` of a profile are an action.

```python
from simplibs.extractor_python.actions import RemovePythonComments, RemovePythonImports

steps = RemovePythonComments() >> RemovePythonImports()

steps("import os\n\n# c\nx = 1  # n\n")                  # -> '\nx = 1\n'
```

The options of the function are the options of the action:

```python
from simplibs.extractor_python.actions import PythonOutline, RemovePythonImports

PythonOutline(docstrings=False)                          # the option `docstrings` of python_outline
RemovePythonImports(on_error="keep")                     # the option `on_error` of remove_python_imports
```

## Where the actions are imported from

`actions/` is a **domain folder** with its own `__all__`; it is not re-exported from the package root. A function and an
action are different kinds of thing and should stay visibly different at the import line:

```python
from simplibs.extractor_python import remove_python_comments               # the function: text -> text
from simplibs.extractor_python.actions import RemovePythonComments         # the action: a step of a pipeline
```

## One direction only

The text flows through, the options (`on_error`, `docstrings`) are configuration. There is no second direction, as there
is in [`simplibs-file`](https://pypi.org/project/simplibs-file/), because a step here has only one thing to carry.

## Thin wrappers

Each action is `create_action(function, main_param="text", class_name=...)` and nothing more — the logic lives once, in
the function. That is why the actions have no cards of their own for errors: an unreadable source raises the same card
as the function (see [Errors of this package](#errors-of-this-package)).

| Action                   | Over                       | Option(s)                         |
|--------------------------|----------------------------|-----------------------------------|
| `RemovePythonComments`   | `remove_python_comments`   | `on_error`                        |
| `RemovePythonDecorators` | `remove_python_decorators` | `on_error`                        |
| `RemovePythonDocstrings` | `remove_python_docstrings` | `on_error`                        |
| `RemovePythonImports`    | `remove_python_imports`    | `on_error`                        |
| `PythonOutline`          | `python_outline`           | `docstrings`, `on_error`          |

`python_comment_spans` has no action: it does not turn a text into a text but into a list of positions, so it is not a
step of a pipeline.

---

## 🧭 Table of Contents

* [`RemovePythonComments`](#removepythoncomments)
* [`RemovePythonDocstrings`](#removepythondocstrings)
* [`RemovePythonImports`](#removepythonimports)
* [`RemovePythonDecorators`](#removepythondecorators)
* [`PythonOutline`](#pythonoutline)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-actions--the-steps-as-pipeline-actions)

---

### `RemovePythonComments`

**Takes the comments out of the Python text flowing in.** Action over
[`remove_python_comments`](logic/README_EXTRACTOR_PYTHON_LOGIC.md#remove_python_comments).

**Main input:** the text (`str`). **Returns:** `str`.

**Options:**

| Name       | Type      | Default   | Description                                                                 |
|------------|-----------|-----------|-----------------------------------------------------------------------------|
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be read, `"keep"` to return it unchanged. |

**Example usage:**

```python
from simplibs.extractor_python.actions import RemovePythonComments, RemovePythonDocstrings

RemovePythonComments()("x = 1  # note\n# alone\n")       # -> 'x = 1\n'

strip_prose = RemovePythonComments() >> RemovePythonDocstrings()
strip_prose('"""Doc."""\nx = 1  # note\n')               # -> 'x = 1\n'

RemovePythonComments(on_error="keep")("print 'x'\n")     # -> "print 'x'\n"      Python 2 stays as it is
```

<details>
<summary>🔍 Under the hood</summary>

```python
RemovePythonComments = create_action(
    remove_python_comments,
    main_param="text",
    class_name="RemovePythonComments",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `RemovePythonDocstrings`

**Takes the docstrings out of the Python text flowing in.** Action over
[`remove_python_docstrings`](logic/README_EXTRACTOR_PYTHON_LOGIC.md#remove_python_docstrings).

**Main input:** the text (`str`). **Returns:** `str`.

**Options:**

| Name       | Type      | Default   | Description                                                                 |
|------------|-----------|-----------|-----------------------------------------------------------------------------|
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be read, `"keep"` to return it unchanged. |

**Example usage:**

```python
from simplibs.extractor_python.actions import RemovePythonDocstrings

RemovePythonDocstrings()('def f():\n    """doc"""\n')   # -> 'def f():\n    pass\n'     a body needs a statement
```

<details>
<summary>🔍 Under the hood</summary>

```python
RemovePythonDocstrings = create_action(
    remove_python_docstrings,
    main_param="text",
    class_name="RemovePythonDocstrings",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `RemovePythonImports`

**Takes the import statements out of the Python text flowing in.** Action over
[`remove_python_imports`](logic/README_EXTRACTOR_PYTHON_LOGIC.md#remove_python_imports).

**Main input:** the text (`str`). **Returns:** `str`.

**Options:**

| Name       | Type      | Default   | Description                                                                 |
|------------|-----------|-----------|-----------------------------------------------------------------------------|
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be read, `"keep"` to return it unchanged. |

**Example usage:**

```python
from simplibs.extractor_python.actions import RemovePythonImports

RemovePythonImports()("import a; x = 1\n")               # -> 'x = 1\n'
```

<details>
<summary>🔍 Under the hood</summary>

```python
RemovePythonImports = create_action(
    remove_python_imports,
    main_param="text",
    class_name="RemovePythonImports",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `RemovePythonDecorators`

**Takes the decorators out of the Python text flowing in.** Action over
[`remove_python_decorators`](logic/README_EXTRACTOR_PYTHON_LOGIC.md#remove_python_decorators).

**Main input:** the text (`str`). **Returns:** `str`.

**Options:**

| Name       | Type      | Default   | Description                                                                 |
|------------|-----------|-----------|-----------------------------------------------------------------------------|
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be read, `"keep"` to return it unchanged. |

**Example usage:**

```python
from simplibs.extractor_python.actions import RemovePythonDecorators

RemovePythonDecorators()("@cache(60)\ndef f(): ...\n")   # -> 'def f(): ...\n'
```

<details>
<summary>🔍 Under the hood</summary>

```python
RemovePythonDecorators = create_action(
    remove_python_decorators,
    main_param="text",
    class_name="RemovePythonDecorators",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `PythonOutline`

**Turns the Python text flowing in into signatures without bodies.** Action over
[`python_outline`](logic/README_EXTRACTOR_PYTHON_LOGIC.md#python_outline).

**Main input:** the text (`str`). **Returns:** `str` — a valid Python outline; an empty string for a file that defines
no class or function.

**Options:**

| Name         | Type      | Default   | Description                                                                          |
|--------------|-----------|-----------|--------------------------------------------------------------------------------------|
| `docstrings` | `bool`    | `True`    | Add the first line of each docstring as a trailing comment.                          |
| `on_error`   | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be read, `"keep"` to return the **whole file**. |

**Example usage:**

```python
from simplibs.extractor_python.actions import PythonOutline

PythonOutline()("def f(): '''d'''\n")                    # -> 'def f(): ...  # d\n'
PythonOutline(docstrings=False)("def f(): '''d'''\n")    # -> 'def f(): ...\n'
```

An outline is usually the **last** step: what comes out is a list of signatures, and nothing after it has a body to work
on. That is why the profile `python/outline` has this action alone.

<details>
<summary>🔍 Under the hood</summary>

```python
PythonOutline = create_action(
    python_outline,
    main_param="text",
    class_name="PythonOutline",
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

This package raises **no cards of its own** here. An unreadable source is the card of the function underneath,
`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID` — see [Errors of the steps](logic/README_EXTRACTOR_PYTHON_LOGIC.md#errors-of-this-package).
A wrong type of an option (`on_error="ignore"`) is a `ValidationError` from
[`simplibs-validate`](https://pypi.org/project/simplibs-validate/), raised by the action that receives it.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-actions--the-steps-as-pipeline-actions)
