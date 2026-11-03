import ast
import pytest
from simplibs.extractor_python.logic._helpers import (
    SourceOffsets,
    cut_statements,
    find_docstrings,
    find_imports,
)


def _cut_imports(text: str) -> str:
    tree = ast.parse(text)
    return cut_statements(text, tree, find_imports(tree), SourceOffsets(text))


def _cut_docstrings(text: str) -> str:
    tree = ast.parse(text)
    return cut_statements(text, tree, find_docstrings(tree), SourceOffsets(text))


def test_nothing_to_cut_gives_the_very_same_text() -> None:
    text = "import os\nx = 1\n"
    tree = ast.parse(text)
    assert cut_statements(text, tree, set(), SourceOffsets(text)) is text
    assert cut_statements(text, tree, [], SourceOffsets(text)) is text


def test_a_statement_on_its_own_line_disappears_with_the_line() -> None:
    assert _cut_imports("import os\nx = 1\n") == "x = 1\n"
    assert _cut_imports("x = 1\nimport os\ny = 2\n") == "x = 1\ny = 2\n"


def test_a_module_may_end_up_empty() -> None:
    assert _cut_imports("import os\n") == ""
    assert _cut_imports("import os\nfrom a import b\n") == ""


def test_a_text_without_a_final_newline() -> None:
    assert _cut_imports("x = 1\nimport os") == "x = 1"

# ---------------------------------------------------------------- the semicolon

@pytest.mark.parametrize(
    "text, expected",
    [
        ("import os; x = 1\n", "x = 1\n"),
        ("x = 1; import os\n", "x = 1\n"),
        ("x = 1; import os; y = 2\n", "x = 1; y = 2\n"),
        ("import a; import b; x = 1\n", "x = 1\n"),
        ("import os ;  x = 1\n", "x = 1\n"),
        ("x = 1 ;  import os\n", "x = 1\n"),
    ],
    ids=["first", "last", "middle", "two-first", "blanks-after", "blanks-before"],
)
def test_the_semicolon_that_joined_the_statement_goes_with_it(text, expected) -> None:
    assert _cut_imports(text) == expected


def test_a_removed_statement_does_not_leave_a_semicolon_behind() -> None:
    assert ";" not in _cut_imports("a = 1; import os\n")


# ---------------------------------------------------------------- a body needs a statement

def test_a_function_left_empty_gets_a_pass() -> None:
    assert _cut_imports("def f():\n    import os\n") == "def f():\n    pass\n"


def test_a_class_left_empty_gets_a_pass() -> None:
    assert _cut_imports("class A:\n    import os\n") == "class A:\n    pass\n"


def test_a_block_that_keeps_a_statement_gets_no_pass() -> None:
    assert _cut_imports("def f():\n    import os\n    return 1\n") == "def f():\n    return 1\n"


def test_both_branches_of_an_if_get_their_own_pass() -> None:
    assert _cut_imports("if x:\n    import a\nelse:\n    import b\n") == "if x:\n    pass\nelse:\n    pass\n"


def test_try_and_except_get_their_own_pass() -> None:
    text = "try:\n    import a\nexcept ImportError:\n    import b\n"
    assert _cut_imports(text) == "try:\n    pass\nexcept ImportError:\n    pass\n"


def test_an_elif_left_empty_gets_a_pass() -> None:
    text = "if a:\n    x = 1\nelif b:\n    import q\n"
    assert _cut_imports(text) == "if a:\n    x = 1\nelif b:\n    pass\n"


def test_a_finally_left_empty_gets_a_pass() -> None:
    text = "try:\n    x = 1\nfinally:\n    import a\n"
    assert _cut_imports(text) == "try:\n    x = 1\nfinally:\n    pass\n"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("for i in x:\n    import a\n", "for i in x:\n    pass\n"),
        ("while x:\n    import a\n", "while x:\n    pass\n"),
        ("with a:\n    import b\n", "with a:\n    pass\n"),
        ("for i in x:\n    pass\nelse:\n    import a\n", "for i in x:\n    pass\nelse:\n    pass\n"),
    ],
    ids=["for", "while", "with", "for-else"],
)
def test_every_kind_of_block_gets_its_pass(text, expected) -> None:
    assert _cut_imports(text) == expected


def test_a_block_on_one_line_gets_a_pass() -> None:
    assert _cut_imports("if x: import a\n") == "if x: pass\n"


def test_two_statements_that_fill_a_block_on_one_line() -> None:
    assert _cut_imports("def f(): import os; import sys\n") == "def f(): pass\n"


def test_a_pass_is_put_where_the_first_statement_stood_so_the_indent_stays() -> None:
    assert _cut_imports("class A:\n    def m(self):\n        import os\n") == "class A:\n    def m(self):\n        pass\n"


def test_two_blocks_one_after_the_other_each_with_its_pass() -> None:
    text = "def f():\n    import a\n\ndef g():\n    import b\n"
    assert _cut_imports(text) == "def f():\n    pass\n\ndef g():\n    pass\n"


# ---------------------------------------------------------------- docstrings

def test_a_docstring_is_cut_with_its_line() -> None:
    assert _cut_docstrings('def f():\n    """Doc."""\n    return 1\n') == "def f():\n    return 1\n"


def test_the_docstring_of_a_module() -> None:
    assert _cut_docstrings('"""Doc."""\nx = 1\n') == "x = 1\n"


def test_a_function_with_only_a_docstring_gets_a_pass() -> None:
    assert _cut_docstrings('def f():\n    """Doc."""\n') == "def f():\n    pass\n"


def test_a_class_with_only_a_docstring_gets_a_pass() -> None:
    assert _cut_docstrings('class A:\n    """Doc."""\n') == "class A:\n    pass\n"


def test_a_docstring_of_several_lines() -> None:
    text = 'def f():\n    """First.\n\n    Second.\n    """\n    return 1\n'
    assert _cut_docstrings(text) == "def f():\n    return 1\n"


def test_a_docstring_with_a_semicolon_after_it() -> None:
    assert _cut_docstrings('def f(): "doc"; return 1\n') == "def f(): return 1\n"


# ---------------------------------------------------------------- what stays

def test_wide_characters_before_the_cut() -> None:
    assert _cut_imports('x = "č€😀"\nimport os\ny = 2\n') == 'x = "č€😀"\ny = 2\n'


def test_the_rest_of_the_text_is_left_exactly_as_it_was() -> None:
    text = "import os\n\n\ndef f(a,b):   # odd   spacing\n    return  a+b\n"
    assert _cut_imports(text) == "\n\ndef f(a,b):   # odd   spacing\n    return  a+b\n"


def test_a_statement_that_is_not_in_the_tree_is_ignored() -> None:
    text = "x = 1\n"
    foreign = ast.parse("import os\n").body[0]
    assert cut_statements(text, ast.parse(text), {foreign}, SourceOffsets(text)) == text


@pytest.mark.parametrize(
    "text",
    [
        "import os\nx = 1\n",
        "def f():\n    import os\n",
        "if x:\n    import a\nelse:\n    import b\n",
        "def f(): import os; import sys\n",
        "x = 1; import os; y = 2\n",
        "try:\n    import a\nexcept ImportError:\n    import b\nfinally:\n    import c\n",
        "class A:\n    import a\n    def m(self):\n        import b\n",
    ],
)
def test_the_result_is_always_valid_python(text) -> None:
    ast.parse(_cut_imports(text))


def test_a_collection_of_any_kind_is_accepted_as_the_targets() -> None:
    text = "import os\nx = 1\n"
    tree = ast.parse(text)
    targets = list(find_imports(tree))
    assert cut_statements(text, tree, targets, SourceOffsets(text)) == "x = 1\n"
    assert cut_statements(text, tree, tuple(targets), SourceOffsets(text)) == "x = 1\n"
    assert cut_statements(text, tree, frozenset(targets), SourceOffsets(text)) == "x = 1\n"
