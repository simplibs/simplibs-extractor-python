import ast
import sys
import pytest
from simplibs.extractor_python.logic._helpers import outline_node


def _outline(source: str, depth: int = 0, docstrings: bool = True) -> list[str]:
    return outline_node(ast.parse(source).body[0], depth, docstrings)


# ---------------------------------------------------------------- functions

def test_a_function_is_its_signature_without_the_body() -> None:
    assert _outline("def f(a, b=1):\n    return a\n") == ["def f(a, b=1): ..."]


def test_annotations_and_the_return_type() -> None:
    assert _outline("def f(a: int = 1, *args: str, **kw: float) -> list[int]:\n    ...\n") == [
        "def f(a: int=1, *args: str, **kw: float) -> list[int]: ..."
    ]


def test_positional_only_and_keyword_only_marks() -> None:
    assert _outline("def f(a, /, b, *, c=2):\n    ...\n") == ["def f(a, /, b, *, c=2): ..."]


def test_an_async_function() -> None:
    assert _outline("async def f():\n    ...\n") == ["async def f(): ..."]


def test_a_function_inside_a_function_is_not_listed() -> None:
    assert _outline("def f():\n    def g(): ...\n    class H: ...\n") == ["def f(): ..."]


def test_decorators_come_first_as_written_by_unparse() -> None:
    assert _outline("@a\n@ b.c(1,2)\ndef f(): ...\n") == ["@a", "@b.c(1, 2)", "def f(): ..."]


# ---------------------------------------------------------------- the first line of the docstring

def test_the_first_line_of_the_docstring_is_a_comment_after_the_signature() -> None:
    assert _outline('def f():\n    """Do it.\n\n    More.\n    """\n') == ["def f(): ...  # Do it."]


def test_docstrings_can_be_switched_off() -> None:
    assert _outline('def f():\n    """Do it."""\n', docstrings=False) == ["def f(): ..."]


def test_a_function_without_a_docstring_has_no_comment() -> None:
    assert _outline("def f(): ...\n", docstrings=True) == ["def f(): ..."]


# ---------------------------------------------------------------- classes

def test_a_class_without_members_is_one_line() -> None:
    assert _outline("class A:\n    x = 1\n") == ["class A: ..."]


@pytest.mark.parametrize(
    "head, expected",
    [
        ("class A(B)", "class A(B): ..."),
        ("class A(B, C)", "class A(B, C): ..."),
        ("class A(B, metaclass=M)", "class A(B, metaclass=M): ..."),
        ("class A(metaclass=M)", "class A(metaclass=M): ..."),
        ("class A(**options)", "class A(**options): ..."),
        ("class A(B[int])", "class A(B[int]): ..."),
    ],
    ids=["one-base", "two-bases", "metaclass", "only-metaclass", "double-star", "generic-base"],
)
def test_the_bases_and_the_keywords_of_a_class(head, expected) -> None:
    assert _outline(f"{head}:\n    x = 1\n") == [expected]


def test_a_class_lists_its_members_one_level_deeper() -> None:
    source = "class A:\n    x = 1\n    def m(self, a: int) -> str:\n        return ''\n    async def n(self): ...\n"
    assert _outline(source) == ["class A:", "    def m(self, a: int) -> str: ...", "    async def n(self): ..."]


def test_members_keep_their_decorators() -> None:
    source = "class A:\n    @property\n    def p(self): ...\n    @staticmethod\n    def s(): ...\n"
    assert _outline(source) == ["class A:", "    @property", "    def p(self): ...", "    @staticmethod", "    def s(): ..."]


def test_a_nested_class_with_its_own_members() -> None:
    source = "class A:\n    class B:\n        def m(self): ...\n    def n(self): ...\n"
    assert _outline(source) == ["class A:", "    class B:", "        def m(self): ...", "    def n(self): ..."]


def test_a_member_in_an_if_block_of_the_class_is_listed() -> None:
    source = "class A:\n    if True:\n        def m(self): ...\n"
    assert _outline(source) == ["class A:", "    def m(self): ..."]


def test_the_docstring_of_a_class_goes_after_its_colon() -> None:
    assert _outline('class A:\n    """The class."""\n    def m(self): ...\n') == ["class A:  # The class.", "    def m(self): ..."]


def test_the_docstring_of_a_class_without_members() -> None:
    assert _outline('class A:\n    """The class."""\n') == ["class A: ...  # The class."]


def test_the_docstrings_of_the_members() -> None:
    source = 'class A:\n    """The class."""\n    def m(self):\n        """Do it."""\n'
    assert _outline(source) == ["class A:  # The class.", "    def m(self): ...  # Do it."]
    assert _outline(source, docstrings=False) == ["class A:", "    def m(self): ..."]


def test_class_decorators() -> None:
    assert _outline("@dataclass(frozen=True)\nclass A:\n    x: int\n") == ["@dataclass(frozen=True)", "class A: ..."]


# ---------------------------------------------------------------- depth

def test_the_depth_indents_every_line_including_the_decorators() -> None:
    assert _outline("@dec\ndef f(): ...\n", depth=2) == ["        @dec", "        def f(): ..."]


def test_the_depth_of_a_class_carries_over_to_its_members() -> None:
    assert _outline("class A:\n    def m(self): ...\n", depth=1) == ["    class A:", "        def m(self): ..."]


# ---------------------------------------------------------------- the result is Python

@pytest.mark.parametrize(
    "source",
    [
        "def f(a, b=1): ...\n",
        'class A(B, metaclass=M):\n    """Doc."""\n    @property\n    def p(self) -> int: ...\n    class N:\n        def x(self): ...\n',
        "@dec\nasync def f(a: int = 1) -> str: ...\n",
    ],
)
@pytest.mark.parametrize("docstrings", [True, False])
def test_the_lines_together_are_valid_python(source, docstrings) -> None:
    ast.parse("\n".join(_outline(source, docstrings=docstrings)))


@pytest.mark.skipif(sys.version_info < (3, 12), reason="type parameters exist since Python 3.12")
def test_type_parameters_stand_after_the_name() -> None:
    assert _outline("def f[T](x: T) -> T: ...\n") == ["def f[T](x: T) -> T: ..."]
    assert _outline("class A[T, U: int](B):\n    def m(self): ...\n") == ["class A[T, U: int](B):", "    def m(self): ..."]
