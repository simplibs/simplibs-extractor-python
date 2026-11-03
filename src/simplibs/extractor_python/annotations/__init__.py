from .OnError import OnError


_DESIGN_NOTES = """
# annotations — Shared Types of simplibs-extractor-python

Plain imports, no `__all__` (the package root decides what is public).

## Internal Components Registry

| Component | Type    | Description                                                             |
| :-------- | :------ | :---------------------------------------------------------------------- |
| `OnError` | Literal | `"raise"` or `"keep"`: what a Python step does with an invalid source.  |

## Not Here
`Span` (a half-open range of characters) is a type of `simplibs-text`; the
steps import it from there.
"""
