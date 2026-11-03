# 🔧 `logic` — The Steps That Read Python

The `logic` package holds the **steps**: plain functions that take a Python source as text and give back a text (or,
for one of them, the positions of the comments). Python is read with **`ast`** and **`tokenize`**, never with a regex —
so a `#` inside a string is not a comment, an `import` inside a docstring is not an import, and `@` in a matrix
multiplication is not a decorator.

```python
from simplibs.extractor_python import (
    python_comment_spans,
    python_outline,
    remove_python_comments,
    remove_python_decorators,
    remove_python_docstrings,
    remove_python_imports,
)
```

All six are exported from the package root. The same steps as pipeline actions live in
[`actions`](../README_EXTRACTOR_PYTHON_ACTIONS.md).

## What each step takes away

One source, five steps:

```python
source = '''"""Tiny demo app."""
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
'''
```

| Step                       | Takes away                                         | Leaves                                              |
|----------------------------|----------------------------------------------------|-----------------------------------------------------|
| `remove_python_comments`   | `# Where the data lives.`, `# relative`, `# build the path` | everything else, strings with a `#` included |
| `remove_python_docstrings` | `"""Tiny demo app."""` and the docstring of `load` | the `#` comments, the code                           |
| `remove_python_imports`    | `import os`, `from pathlib import Path`            | the names that were imported, still used below       |
| `remove_python_decorators` | `@cache(60)`                                       | the function it decorated                            |
| `python_outline`           | every body                                         | `@cache(60)` and `def load(...) -> str: ...  # Read one file.` |

## The contract all of them share

| Rule                                | What it means                                                                                        |
|-------------------------------------|------------------------------------------------------------------------------------------------------|
| **Text in, text out**               | `str` → `str`. `python_comment_spans` returns the positions of the comments, `list[Span]`.          |
| **Cut by position, nothing else**   | A removal cuts exactly the characters of what it finds; the rest of the file stays as it was written — spacing, quotes, line breaks. (`python_outline` is the exception: it writes new text from the tree.) |
| **The tree stays**                  | For a text that parses, the syntax tree of the result is the tree of the original **without** what the step removes (a `pass` stands in for a body left empty). |
| **Nothing to do, nothing changed**  | A text without anything to remove comes back as the very same text.                                  |
| **Idempotent**                      | A second run finds nothing and returns the same text.                                                |
| **`on_error`**                      | `"raise"` (the default) or `"keep"` — see [`OnError`](../README_EXTRACTOR_PYTHON_ANNOTATIONS.md#onerror). |
| **`\n` only**                       | A text with `\r` is refused (`on_error` decides how): `ast` counts a lone `\r` as a line end and the cutting does not. The extractor never gives one — its reader hands over `\n` only. |
| **Valid for the running Python**    | "Valid" means valid for the interpreter that runs the step. Source that uses syntax newer than that interpreter (a `def f[T]()` on Python 3.11) is a source it cannot read. |

The output of a removal is **for reading, not for running**: a decorator can change what a function *is*
(`@property`, `@staticmethod`), an import line says where a name comes from. That is the point of the profiles that use
them.

## Order in a chain

The removals do not need each other, but this order is the one the presets use and the one that leaves the least
behind:

```
comments  →  docstrings  →  imports  →  decorators  →  whitespace
```

Comments come first because a comment after a decorator (`@dec  # note`) is not part of the decorator and would stay
behind as a lone `# note`; whitespace comes **last**, because the holes the other steps leave are the thing it tidies.

## Under the hood of the package

The steps share a few private tools in `logic/_helpers/` and one card in `logic/_validations/`. They have no cards of
their own here — they are not part of the interface — but they explain why the steps behave as they do:

| Helper                    | What it does                                                                                           |
|---------------------------|--------------------------------------------------------------------------------------------------------|
| `guarded_parse`           | The one place where reading fails. Catches `SyntaxError`, `ValueError`, `RecursionError` and `tokenize.TokenError`, and lets `on_error` decide. Anything else is a bug and is not hidden. |
| `parse_python`            | `ast.parse` under that guard; `None` means "leave the text alone".                                     |
| `SourceOffsets`           | Turns the positions of `ast` (columns in **UTF-8 bytes**) and `tokenize` (characters) into offsets in the text, so `é` or `€` in front of a node does not shift a cut. |
| `cut_statements`          | Removes simple statements and keeps the syntax: gives an emptied block a `pass`, takes a `;` with a statement that shared its line. |
| `find_docstrings`, `find_imports`, `find_decorator_spans` | Find **what** to cut.                                                      |
| `collect_definitions`, `outline_node`, `first_doc_line`, `format_type_params` | Build the outline.                                       |
| `describe_source_failure` | From an exception of the parser to a reason and a line.                                                |
| `raise_python_source_error` | The card `CODE_EXTRACTOR_PYTHON_SOURCE_INVALID` (see [Errors of this package](#errors-of-this-package)). |

---

## 🧭 Table of Contents

* [`python_comment_spans`](#python_comment_spans)
* [`remove_python_comments`](#remove_python_comments)
* [`remove_python_docstrings`](#remove_python_docstrings)
* [`remove_python_imports`](#remove_python_imports)
* [`remove_python_decorators`](#remove_python_decorators)
* [`python_outline`](#python_outline)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../../README.md#-logic--the-steps-that-read-python)

---

### `python_comment_spans`

**Finds the comments of a Python source** — where they are, as spans that `remove_spans` can cut.

The tokenizer marks every `#` comment; the span of each one runs from the **blanks in front of it** to its end.

**Parameters:**

| Name       | Type      | Default   | Description                                                                              |
|------------|-----------|-----------|------------------------------------------------------------------------------------------|
| `text`     | `str`     | *(required)* | The Python source.                                                                    |
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be tokenized, `"keep"` for no spans. *(keyword-only)* |

**Returns:** `list[Span]` — a half-open `(start, end)` for each comment, in the order of the file. A text with no comment
(or one that could not be read, with `on_error="keep"`) gives `[]`.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be tokenized and `on_error` is `"raise"`.
* `ValidationError` — `text` is not a `str`, or `on_error` is not one of the two values.

**Example usage:**

```python
from simplibs.extractor_python import python_comment_spans
from simplibs.text import remove_spans

text = "x = 1  # a\n# b\ns = '# not a comment'\n"

spans = python_comment_spans(text)
spans                                                    # -> [(5, 10), (11, 14)]
[text[start:end] for start, end in spans]                # -> ['  # a', '# b']       the blanks in front are part of the span

remove_spans(text, spans)                                # -> "x = 1\ns = '# not a comment'\n"

python_comment_spans("x = 'abc\n")                       # raises ParamError — an unterminated string
python_comment_spans("x = 'abc\n", on_error="keep")      # -> []
```

**Why `tokenize` and not a regex.** A `#` inside a string (`"a # b"`, `'''# not a comment'''`) is not a comment, and
telling the two apart is the tokenizer's job. A regex gets it wrong exactly in the files where it matters.

**The blanks in front.** `x = 1  # note` is cut to `x = 1`, not to `x = 1  `. A comment on a line of its own is taken
with its indentation, and the cut then removes the empty line.

**Shebang and coding line.** `#!/usr/bin/env python` and `# -*- coding: utf-8 -*-` are comments to the tokenizer and go
with the rest: the output is for reading, not for running.

**What it needs.** Only that the text can be **tokenized**, not that it is valid Python 3. A file that `ast` refuses may
still have its comments found.

<details>
<summary>🔍 Under the hood</summary>

```python
def _collect_comment_spans(text: str) -> list[Span]:

    # 1. Every COMMENT token, with the blanks in front of it
    offsets = SourceOffsets(text)
    spans: list[Span] = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        start = offsets.token_offset(*token.start)
        end = offsets.token_offset(*token.end)
        while start > 0 and text[start - 1] in " \t":
            start -= 1
        spans.append((start, end))

    return spans


@validate_call
def python_comment_spans(text: str, *, on_error: OnError = "raise") -> list[Span]:

    # 1. Tokenize under the guard
    spans = guarded_parse(text, on_error, _collect_comment_spans)

    # 2. A text that could not be read has no spans
    return spans or []
```

`tokenize` reports positions as `(row, column)`; `SourceOffsets.token_offset` turns each into an offset in the text.
The loop that walks back over `" \t"` is the whole "blanks in front" rule. `guarded_parse` runs the collector and decides
what a failure means, so the step itself never has a `try`.

</details>

[▲ Back to top](#-table-of-contents)

---

### `remove_python_comments`

**Removes all comments from a Python source.**

A step of the profiles `python/code-clean`, `python/src-clean` and `python/code-no-imports`. It finds the comments with
[`python_comment_spans`](#python_comment_spans) and cuts them.

**Parameters:**

| Name       | Type      | Default   | Description                                                                              |
|------------|-----------|-----------|------------------------------------------------------------------------------------------|
| `text`     | `str`     | *(required)* | The Python source.                                                                    |
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be tokenized, `"keep"` to return it unchanged. *(keyword-only)* |

**Returns:** `str` — the text without comments. A line that held only a comment disappears.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be tokenized and `on_error` is `"raise"`.
* `ValidationError` — a wrong type of an argument.

**Example usage:**

```python
from simplibs.extractor_python import remove_python_comments

remove_python_comments("x = 1  # note\n# alone\ny = '# not a comment'\n")
# -> "x = 1\ny = '# not a comment'\n"

remove_python_comments("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nx = 1\n")      # -> 'x = 1\n'
remove_python_comments("# a\n# b\n")                                                  # -> ''
remove_python_comments("x = 1\n")                                                     # -> 'x = 1\n'   the very same text

text = remove_python_comments("x = 1  # a\n")
remove_python_comments(text) == text                                                  # -> True     a second run finds nothing
```

**The guarantee.** For a text that parses, the syntax tree of the result is **the same** as the tree of the original:
nothing but comments (and the blanks and empty lines they left) is removed. Docstrings are strings, not comments, and
stay.

**An empty line that was already there stays.** Only a line that is blank **because of** the removal disappears — the
rule of `remove_spans`.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def remove_python_comments(text: str, *, on_error: OnError = "raise") -> str:

    # 1. Find the comments
    spans = python_comment_spans(text, on_error=on_error)

    # 2. Cut them; strings that merely contain a `#` were never found
    return remove_spans(text, spans)
```

Two lines: **finding** and **cutting** are separate jobs. `remove_spans` — the shared primitive of
[`simplibs-text`](https://pypi.org/project/simplibs-text/) — merges overlapping spans, ignores empty ones and drops the
lines the cut emptied. With `on_error="keep"` an unreadable text has no spans, and `remove_spans` returns it as it came.

</details>

[▲ Back to top](#-table-of-contents)

---

### `remove_python_docstrings`

**Removes the docstrings of a Python source:** of the module, its classes and its functions.

A step of the profiles `python/code-clean`, `python/src-clean` and `python/code-no-imports`.

**Parameters:**

| Name       | Type      | Default   | Description                                                                              |
|------------|-----------|-----------|------------------------------------------------------------------------------------------|
| `text`     | `str`     | *(required)* | The Python source.                                                                    |
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged. *(keyword-only)* |

**Returns:** `str` — the text without docstrings. A body left empty gets a `pass`.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be parsed and `on_error` is `"raise"`.
* `ValidationError` — a wrong type of an argument.

**Example usage:**

```python
from simplibs.extractor_python import remove_python_docstrings

remove_python_docstrings('"""Module doc."""\nx = 1\n')                              # -> 'x = 1\n'          a module may be empty

remove_python_docstrings('class A:\n    """doc"""\n\ndef f():\n    """doc"""\n')
# -> 'class A:\n    pass\n\ndef f():\n    pass\n'                                    a body needs a statement

remove_python_docstrings("def f(): '''doc'''\n")                                      # -> 'def f(): pass\n'   even on the line of the `def`

remove_python_docstrings('def f():\n    x = 1\n    "not a docstring"\n    return x\n')
# -> 'def f():\n    x = 1\n    "not a docstring"\n    return x\n'                  a string in the middle stays
```

**What a docstring is.** The string that is the **first statement** of a module, a class or a function — the same rule as
`ast.get_docstring`, applied to the whole tree at once. Other strings, even alone on their line, are left; so is an
f-string, because it is built at run time.

**A body needs a statement.** `def f():` with only a docstring is `def f(): pass` afterwards; so is a class. A module may
be empty and gets no `pass`.

**A statement, not a line.** A docstring may share its line or be wrapped in parentheses; the span of the statement covers
both.

**The guarantee.** For a text that parses, the syntax tree of the result equals the tree of the original with the
docstring statements taken out (and a `Pass` where a body would be empty).

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def remove_python_docstrings(text: str, *, on_error: OnError = "raise") -> str:

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut the docstring statements
    return cut_statements(text, tree, find_docstrings(tree), SourceOffsets(text))
```

`find_docstrings` walks the tree and collects the first statement of every module, class and function when it is a string
constant. `cut_statements` removes them: it gives each block that would be left empty a `pass` — inserted in front of the
first statement of the block, so the `pass` takes the place of the removed text, indentation and all — and takes the `;`
with a statement that shared its line. The same primitive serves `remove_python_imports`.

</details>

[▲ Back to top](#-table-of-contents)

---

### `remove_python_imports`

**Removes the import statements of a Python source, at any depth.**

The step of `python/code-no-imports`: the logic without its dependencies.

**Parameters:**

| Name       | Type      | Default   | Description                                                                              |
|------------|-----------|-----------|------------------------------------------------------------------------------------------|
| `text`     | `str`     | *(required)* | The Python source.                                                                    |
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged. *(keyword-only)* |

**Returns:** `str` — the text without imports. A body left empty gets a `pass`; `import a; x = 1` keeps `x = 1`.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be parsed and `on_error` is `"raise"`.
* `ValidationError` — a wrong type of an argument.

**Example usage:**

```python
from simplibs.extractor_python import remove_python_imports

remove_python_imports("import os\nfrom pathlib import Path\nx = 1\n")      # -> 'x = 1\n'

# on one line with another statement — the `;` goes with the import
remove_python_imports("import a; x = 1\ny = 2; import b\n")                # -> 'x = 1\ny = 2\n'

# at any depth, and an emptied block gets a `pass`
remove_python_imports(
    "def f():\n    import os\n\ntry:\n    import ujson\nexcept ImportError:\n    import json\n"
)
# -> 'def f():\n    pass\n\ntry:\n    pass\nexcept ImportError:\n    pass\n'

remove_python_imports("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from x import Y\n\nz = 1\n")
# -> 'if TYPE_CHECKING:\n    pass\n\nz = 1\n'

remove_python_imports("from __future__ import annotations\nx = 1\n")       # -> 'x = 1\n'
remove_python_imports("s = 'é€'; import os\nx = 1\n")                       # -> "s = 'é€'\nx = 1\n"    non-ASCII text in front is no problem
```

**Every import, not only the top ones.** `try: import ujson / except ImportError: import json`, `if TYPE_CHECKING:` and
imports inside a function are all imports. Leaving the nested ones would leave a file that still names its dependencies.

**`from __future__`.** It is an `ImportFrom` and goes with the rest. For reading the code, a
`from __future__ import annotations` carries no information.

**What is left behind.** Names that were imported are still used further down; the reader of the output sees code that
refers to `Path` or `np` without the line that says where they come from. That is what the profile is for: the logic, not
the wiring.

**A blank line that was there stays.** After the first line of a file is removed, a blank line that followed it is now the
first line. The presets that use this step finish with `COMPACT`, which removes it.

**The guarantee.** For a text that parses, the syntax tree of the result equals the tree of the original without the
`Import` and `ImportFrom` statements (and a `Pass` where a body would be empty).

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def remove_python_imports(text: str, *, on_error: OnError = "raise") -> str:

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut the import statements
    return cut_statements(text, tree, find_imports(tree), SourceOffsets(text))
```

```python
def find_imports(tree: ast.Module) -> set[ast.stmt]:
    # 1. Both kinds, wherever they stand
    return {node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))}
```

`ast.walk` visits the whole tree, so depth is not a question. Everything else — the `pass`, the `;`, the offsets — is
`cut_statements`, shared with [`remove_python_docstrings`](#remove_python_docstrings).

</details>

[▲ Back to top](#-table-of-contents)

---

### `remove_python_decorators`

**Removes the decorators of every class and function of a Python source.**

A step of the profile `python/code-no-imports`: `@app.route(...)`, `@dataclass` and `@property` describe how a function
is registered or wrapped, not what it does.

**Parameters:**

| Name       | Type      | Default   | Description                                                                              |
|------------|-----------|-----------|------------------------------------------------------------------------------------------|
| `text`     | `str`     | *(required)* | The Python source.                                                                    |
| `on_error` | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged. *(keyword-only)* |

**Returns:** `str` — the text without decorators; the lines they stood on disappear.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be parsed and `on_error` is `"raise"`.
* `ValidationError` — a wrong type of an argument.

**Example usage:**

```python
from simplibs.extractor_python import remove_python_decorators

remove_python_decorators("@app.route('/')\n@cache(60)\ndef index():\n    pass\n")
# -> 'def index():\n    pass\n'

remove_python_decorators("class A:\n    @property\n    def x(self):\n        return 1\n")
# -> 'class A:\n    def x(self):\n        return 1\n'

remove_python_decorators("@(lambda f: f)\ndef g(): ...\n")                    # -> 'def g(): ...\n'     a bracketed decorator, Python 3.9+

remove_python_decorators("@dec  # note\ndef f(): ...\n")                      # -> '  # note\ndef f(): ...\n'    the comment is not a part of it
```

**Semantics change.** A decorator can change what a function **is** (`@property`, `@staticmethod`, `@contextmanager`).
The output is for reading; it is not meant to be run.

**A comment after a decorator stays.** It is not a part of the decorator. Comments are a step of their own, normally run
first — see [the order in a chain](#order-in-a-chain).

**The guarantee.** For a text that parses, the syntax tree of the result equals the tree of the original with every
`decorator_list` emptied.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def remove_python_decorators(text: str, *, on_error: OnError = "raise") -> str:

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. Cut each decorator from its `@`
    return remove_spans(text, find_decorator_spans(text, tree, SourceOffsets(text)))
```

```python
def _line_start(text: str, position: int) -> int:
    # The offset where the line holding `position` begins
    ...

def _end_of_line(text: str, position: int) -> int:
    # The offset of the line break that ends the line holding `position`
    ...

def _count_opening_brackets(text: str, begin: int, stop: int) -> int:
    # The `(` in text[begin:stop], leaving out comments
    ...

def _skip_filler(text: str, position: int) -> int:
    # The first character from `position` on that is no blank, line break or comment
    ...


def find_decorator_spans(text: str, tree: ast.Module, offsets: SourceOffsets) -> list[Span]:

    # 1. Every decorator of every class and function
    spans: list[Span] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for decorator in node.decorator_list:
            start, end = offsets.span_of(decorator)

            # 2. The `@` stands in front of the expression; an `@` with a `#` before it on its line is in a comment
            at = text.rfind("@", 0, start)
            while "#" in text[_line_start(text, at):at]:
                at = text.rfind("@", 0, at)

            # 3. `@(factory)`: the node does not include its own brackets, so the closing ones are taken too
            for _ in range(_count_opening_brackets(text, at + 1, start)):
                end = _skip_filler(text, end) + 1

            spans.append((at, end))

    return spans
```

`ast` gives the position of the decorator's **expression**, not of the `@`; the span has to start at the `@` or what is
left is a line holding a lone `@`. The nearest `@` in front of the expression is the decorator's own (`rfind`) — unless
it stands in a comment inside the brackets, which the `#` in front of it on its line gives away. For `@(lambda f: f)` the
expression node starts after the `(` and ends before the `)`, so the opening brackets between the `@` and the
expression are counted and the same number of closing ones is taken after it. Comments inside the brackets are skipped
on the way, so a `(` or `)` written in one is never mistaken for a real bracket.

</details>

[▲ Back to top](#-table-of-contents)

---

### `python_outline`

**Writes an overview of a Python source:** its classes and functions as signatures without bodies.

The step of the profile `python/outline`: what a file offers, without how it does it. For giving a large project to a
reader with a limited window, the signatures are most of what is needed to ask the right questions.

**Parameters:**

| Name         | Type      | Default   | Description                                                                            |
|--------------|-----------|-----------|----------------------------------------------------------------------------------------|
| `text`       | `str`     | *(required)* | The Python source.                                                                  |
| `docstrings` | `bool`    | `True`    | Add the first line of each docstring as a trailing comment. *(keyword-only)*           |
| `on_error`   | `OnError` | `"raise"` | `"raise"` for a card when the text cannot be parsed, `"keep"` to return it unchanged — the **whole file**, not an outline. *(keyword-only)* |

**Returns:** `str` — the outline, valid Python; an **empty string** for a file that defines no class or function.

**Raises:**

* `ParamError` (`CODE_EXTRACTOR_PYTHON_SOURCE_INVALID`) — the text cannot be parsed and `on_error` is `"raise"`.
* `ValidationError` — a wrong type of an argument.

**Example usage:**

```python
from simplibs.extractor_python import python_outline

source = '''@dataclass
class Box(Base):
    """A box.

    More text.
    """

    def size(self, n: int = 1) -> int:
        """Return the size."""
        return n
'''

python_outline(source)
# -> '@dataclass\nclass Box(Base):  # A box.\n    def size(self, n: int=1) -> int: ...  # Return the size.\n'

python_outline(source, docstrings=False)
# -> '@dataclass\nclass Box(Base):\n    def size(self, n: int=1) -> int: ...\n'

python_outline("x = 1\n")                                # -> ''       nothing is defined

python_outline("class C(A, metaclass=M, **o):\n    x = 1\n    class In: ...\n    def m(self): ...\n")
# -> 'class C(A, metaclass=M, **o):\n    class In: ...\n    def m(self): ...\n'

python_outline("if True:\n    def g(): ...\ndef outer():\n    def inner(): ...\n")
# -> 'def g(): ...\ndef outer(): ...\n'                 `g` is a member of the module, `inner` is a detail of `outer`
```

**What is listed.** The classes and functions of the module; the methods and nested classes of a class; definitions
inside `if`, `try`, `with`, `for`, `while` and `match` blocks, which are looked through but not reported. A function inside a
function is **not** listed: it is that function's own detail. A class with no members is one line (`class A: ...`). If
both branches of an `if` define `f`, both are listed — the condition is lost, and Python allows a redefinition.

**Written from the tree.** Signatures come from `ast.unparse`, not from the source text, so spacing and line breaks are
normalised (`a: int = 1` is written `a: int=1`) and the output is always valid Python. A default value, an annotation or
a keyword is always what the source says, never a guess of a regex. Type parameters (`def first[T](items: list[T])`) are
written too — they exist from Python 3.12.

**A docstring as a comment.** `# First line of the docstring` after the signature — so there is no string to quote,
escape or close. The line is the first non-empty one; a docstring that starts with a blank line is quoted from its first
real line.

**Not the same as the other steps.** It does not cut the original: it **writes** a new text. So it is the one step that
changes the spacing, and the one whose `on_error="keep"` returns something different from what it would have returned
(the whole file instead of an outline).

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def python_outline(text: str, *, docstrings: bool = True, on_error: OnError = "raise") -> str:

    # 1. Parse; a text that could not be read is not touched
    tree = parse_python(text, on_error)
    if tree is None:
        return text

    # 2. The outline of every definition of the module
    lines: list[str] = []
    for definition in collect_definitions(tree.body):
        lines.extend(outline_node(definition, 0, docstrings))

    return "\n".join(lines) + "\n" if lines else ""
```

`collect_definitions` returns the definitions of one level in source order, looking through blocks:

```python
_DEFINITIONS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
_BLOCK_FIELDS = ("body", "handlers", "orelse", "finalbody", "cases")
_CLAUSES = (ast.ExceptHandler, ast.match_case)


def collect_definitions(body: Sequence[ast.stmt]) -> list[ast.stmt]:

    # 1. A definition counts; a block that holds definitions is looked through
    found: list[ast.stmt] = []
    for statement in body:
        if isinstance(statement, _DEFINITIONS):
            found.append(statement)
            continue
        for field in _BLOCK_FIELDS:
            inner = getattr(statement, field, None)
            if not isinstance(inner, list):
                continue
            for item in inner:
                # 2. An `except` handler and a `case` hold a body of their own; anything else is a statement
                found.extend(collect_definitions(item.body if isinstance(item, _CLAUSES) else [item]))

    return found
```

`outline_node` writes one definition — the decorators as written, a function as a signature with `: ...`, a class as a
header followed by its members:

```python
def outline_node(node, depth: int, docstrings: bool) -> list[str]:

    # 1. The decorators, as written
    pad = "    " * depth
    lines = [f"{pad}@{ast.unparse(decorator)}" for decorator in node.decorator_list]
    note = first_doc_line(node) if docstrings else ""
    params = format_type_params(node)

    # 2. A function: its signature, no body
    if not isinstance(node, ast.ClassDef):
        keyword = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        lines.append(f"{pad}{keyword} {node.name}{params}({ast.unparse(node.args)}){returns}: ...{note}")
        return lines

    # 3. A class: its bases and keywords (`metaclass=M`, `**options`)
    bases = [ast.unparse(base) for base in node.bases]
    bases += [
        f"{keyword.arg}={ast.unparse(keyword.value)}" if keyword.arg else f"**{ast.unparse(keyword.value)}"
        for keyword in node.keywords
    ]
    head = f"class {node.name}{params}" + (f"({', '.join(bases)})" if bases else "")

    # 4. The members are listed under it; a class with none is one line
    members = collect_definitions(node.body)
    if not members:
        lines.append(f"{pad}{head}: ...{note}")
        return lines
    lines.append(f"{pad}{head}:{note}")
    for member in members:
        lines.extend(outline_node(member, depth + 1, docstrings))

    return lines
```

`first_doc_line` uses `splitlines()` and not `split("\n")`: a docstring can hold a `\r` or a form feed written as an
escape, and cut by `\n` only such a character would end up in the output, where `ast` would take it for a line end and
turn the rest of the comment into code.

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

All six steps raise **one** card, and only when `on_error="raise"`:

| Error name                             | Class        | Wraps        | Raised when                                                                          |
|----------------------------------------|--------------|--------------|--------------------------------------------------------------------------------------|
| `CODE_EXTRACTOR_PYTHON_SOURCE_INVALID` | `ParamError` | `ValueError` | The text cannot be read as Python: a syntax error, a bad indentation, an unterminated string or bracket, a null character, line endings other than `\n`. |

```python
remove_python_imports("print 'hello'\n")
# raises ParamError: The text is not Python source I can read: Missing parentheses in call to 'print'. ... (line 1).
```

The card shows the **offending line** (the start of the text when no line is known), not the whole text — a card that
prints a whole file is not one anybody reads. It says what is expected (*valid Python 3 source with `\n` line endings*)
and gives three ways out: fix the file; leave it out of the extraction with an `exclude` rule of the profile; or pass
`on_error="keep"`.

**What the extractor does with it.** A step that raises marks **that file** `error` in the report (`transform failed: ...`)
and the run goes on with the next file; the run is unsuccessful. With `on_error="keep"` the step never gets here.

A wrong **type** of an argument (`text=5`, `on_error="ignore"`) is a `ValidationError` from
[`simplibs-validate`](https://pypi.org/project/simplibs-validate/), as everywhere in the family.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logic--the-steps-that-read-python)
