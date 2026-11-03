from typing import Literal


OnError = Literal["raise", "keep"]
"""What a Python step does with a source it cannot read: raise a card, or return the text unchanged."""


_DESIGN_NOTES = """
# OnError — What to Do With a Source That Is Not Valid

## Purpose
The type of the `on_error` option of the Python steps: a file that is not valid
Python (an old Python 2 file, a template with `{{ }}` in it, a half-written
module) cannot be read by `ast` or `tokenize`.

## The Two Answers
* `"raise"` — the step raises a card. The extractor marks that file `error`,
  names the reason in the report and goes on with the next file. The default:
  nothing is hidden.
* `"keep"` — the text comes back unchanged and nothing is said. For your own
  profile, when "not cleaned" is better than "not there".

## Why a Literal
A typo (`"Raise"`, `"ignore"`) fails at the signature, not deep inside a step.
"""
