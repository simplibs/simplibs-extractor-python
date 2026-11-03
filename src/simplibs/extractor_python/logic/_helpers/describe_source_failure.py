import tokenize


def describe_source_failure(exc: Exception) -> tuple[str, int | None]:
    """Say in words why a text could not be read, and where.

    Args:
        exc: What the parser raised.

    Returns:
        `(reason, line)`; the line is `None` when the exception does not carry one.
    """

    # 1. A syntax error knows its message and its line
    if isinstance(exc, SyntaxError):
        return (exc.msg or "invalid syntax"), exc.lineno

    # 2. The tokenizer puts the message and `(line, column)` into its arguments
    if isinstance(exc, tokenize.TokenError):
        reason = str(exc.args[0]) if exc.args else "tokenizing failed"
        line = exc.args[1][0] if len(exc.args) > 1 and isinstance(exc.args[1], tuple) else None
        return reason, line

    # 3. The rest has only a text
    return (str(exc) or type(exc).__name__), None


_DESIGN_NOTES = """
# describe_source_failure — From an Exception to a Sentence

## Purpose
`SyntaxError`, `tokenize.TokenError` and `ValueError` say the same thing in
three shapes. The card needs one: a reason and a line.
"""
