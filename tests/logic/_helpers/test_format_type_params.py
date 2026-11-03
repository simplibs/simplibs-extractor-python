import ast
import sys
import pytest
from simplibs.extractor_python.logic._helpers import format_type_params

NEW_SYNTAX = pytest.mark.skipif(sys.version_info < (3, 12), reason="type parameters exist since Python 3.12")


def _node(source: str):
    return ast.parse(source).body[0]


def test_a_function_without_type_parameters_gives_nothing() -> None:
    assert format_type_params(_node("def f(a): ...\n")) == ""


def test_a_class_without_type_parameters_gives_nothing() -> None:
    assert format_type_params(_node("class A(B): ...\n")) == ""


def test_a_node_that_has_no_such_field_gives_nothing() -> None:
    """Older Pythons have no `type_params` at all, and a node of another kind has none either."""
    assert format_type_params(ast.Pass()) == ""


@NEW_SYNTAX
def test_one_parameter() -> None:
    assert format_type_params(_node("def f[T](x: T): ...\n")) == "[T]"


@NEW_SYNTAX
def test_several_parameters_with_a_bound() -> None:
    assert format_type_params(_node("class A[T, U: int]: ...\n")) == "[T, U: int]"


@NEW_SYNTAX
def test_star_and_double_star_parameters() -> None:
    assert format_type_params(_node("def f[*Ts, **P](): ...\n")) == "[*Ts, **P]"


@NEW_SYNTAX
def test_a_constraint_tuple() -> None:
    assert format_type_params(_node("def f[T: (int, str)](x: T): ...\n")) == "[T: (int, str)]"


@NEW_SYNTAX
def test_an_async_function() -> None:
    assert format_type_params(_node("async def f[T](x: T): ...\n")) == "[T]"
