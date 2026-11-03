from .annotations import OnError
from .logic import (
    python_comment_spans,
    python_outline,
    remove_python_comments,
    remove_python_decorators,
    remove_python_docstrings,
    remove_python_imports,
)
from .plugin import register_all


__all__ = [
    # steps
    "python_comment_spans",
    "python_outline",
    "remove_python_comments",
    "remove_python_decorators",
    "remove_python_docstrings",
    "remove_python_imports",
    # add-on of the extractor
    "register_all",
    # types
    "OnError",
]


_DESIGN_NOTES = """
# simplibs-extractor-python — Package Root

## Purpose
The add-on that teaches `simplibs-extractor` about Python: file rules for
Python projects, the steps that clean the source (comments, docstrings,
imports, decorators), an outline step and five ready profiles. Install it and
the profiles are there:

    simplibs-extractor python src-clean my_project

## What the Root Exports
The steps as plain functions (`str -> str`), `register_all` (the target of the
entry point `simplibs.extractor.plugins`) and the annotation meant for the
caller's own signatures:

    from simplibs.extractor_python import remove_python_comments, python_outline, OnError

## What the Root Deliberately Does NOT Export
Four domain folders with their own `__all__`, imported through their domain:

    from simplibs.extractor_python.actions import RemovePythonComments
    from simplibs.extractor_python.file_rules import PYTHON_BASE, build_python_base
    from simplibs.extractor_python.presets import PYTHON_CLEAN
    from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN

and the internals: `_helpers/` and `_validations/` inside the domains.

## Spans
The steps find ranges of characters as `simplibs.text.Span`. The type is not
defined here, it is taken from `simplibs-text`.

## Layering
`annotations` ← `constants` ← `file_rules` ← `logic` ← `actions` ← `presets` ← `profiles` ← `plugin`.
Each layer imports only from the layers on its left; the root imports from the ones it exports.

## `__all__`
Defined here and in the domain folders (`actions`, `file_rules`, `presets`,
`profiles`) only; the layers inside them use plain imports.
"""
