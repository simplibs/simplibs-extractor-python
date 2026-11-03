# 🏷️ `annotations` — Shared Types

The `annotations` package holds the **one type** of this library that you may want in your own signatures:
`OnError`, the type of the `on_error` option of every Python step.

```python
from simplibs.extractor_python import OnError
```

`OnError` is exported from the package root, because a function of yours that wraps a step usually passes the
option on:

```python
from simplibs.extractor_python import OnError, remove_python_imports

def strip_dependencies(text: str, *, on_error: OnError = "keep") -> str:
    return remove_python_imports(text, on_error=on_error)
```

## A type that is not here

The steps find **ranges of characters** and hand them to `remove_spans`. That range is `Span`, a type of
[`simplibs-text`](https://pypi.org/project/simplibs-text/), and this library takes it from there instead of
defining a second one:

```python
from simplibs.text import Span
```

---

## 🧭 Table of Contents

* [`OnError`](#onerror)

[⬅️ Back to main README](../README.md#-annotations-and-constants)

---

### `OnError`

**What a Python step does with a source it cannot read.**

A file that is not valid Python — an old Python 2 file, a template, a half-written module — cannot be read by `ast`
or `tokenize`. The step has two honest answers, and the type names them.

**Values:**

| Value     | What the step does                                                                                           |
|-----------|--------------------------------------------------------------------------------------------------------------|
| `"raise"` | Raises a card (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`). The default: nothing is hidden. The extractor marks **that file** `error`, names the reason in the report and goes on with the next file. |
| `"keep"`  | Returns the text **unchanged** and says nothing. For a profile of your own, when "not cleaned" is better than "not there". |

**Kind:** `Literal["raise", "keep"]`.

**Example usage:**

```python
from simplibs.extractor_python import remove_python_imports

broken = "print 'hello'\n"                               # Python 2

remove_python_imports(broken)                            # raises ParamError (CODE_EXTRACTOR_PYTHON_SOURCE_INVALID)
remove_python_imports(broken, on_error="keep")           # -> "print 'hello'\n"        the same text back
remove_python_imports(broken, on_error="Raise")          # raises ValidationError — a typo fails at the signature
```

**Why a `Literal`.** A typo (`"Raise"`, `"ignore"`) fails where the option is passed, not deep inside a step.

**Which default.** `"raise"` is the default of every step, so a file the profile could not clean never slips into
the output looking clean. `"keep"` is a decision you make **for a profile**, knowing that some files will stay as they
were.

<details>
<summary>🔍 Under the hood</summary>

```python
OnError = Literal["raise", "keep"]
```

Nothing more. The steps check it through `@validate_call`, which reads the `Literal` from the signature, and one
function — `guarded_parse` — turns it into behaviour: `"keep"` makes it return `None` (the caller then returns the text
as it was), `"raise"` makes it raise the card.

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-annotations-and-constants)
