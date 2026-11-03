import ast
import pytest
from simplibs.extractor_python.logic._helpers import collect_definitions


def _names(source: str) -> list[str]:
    return [node.name for node in collect_definitions(ast.parse(source).body)]


def test_nothing_to_find_gives_an_empty_list() -> None:
    assert collect_definitions([]) == []
    assert _names("x = 1\nprint(x)\n") == []


def test_classes_and_functions_come_in_source_order() -> None:
    assert _names("def a(): ...\nclass B: ...\nasync def c(): ...\ndef d(): ...\n") == ["a", "B", "c", "d"]


def test_the_result_holds_the_nodes_themselves() -> None:
    tree = ast.parse("def a(): ...\nclass B: ...\n")
    assert collect_definitions(tree.body) == [tree.body[0], tree.body[1]]


def test_what_is_inside_a_definition_is_not_reported() -> None:
    """A function in a function is the detail of the outer one; a method is found when the class body is asked."""
    assert _names("def f():\n    def g(): ...\n    class H: ...\n") == ["f"]
    assert _names("class A:\n    def m(self): ...\n") == ["A"]


def test_the_body_of_a_class_gives_its_members() -> None:
    tree = ast.parse("class A:\n    x = 1\n    def m(self): ...\n    class N: ...\n")
    assert [node.name for node in collect_definitions(tree.body[0].body)] == ["m", "N"]


@pytest.mark.parametrize(
    "source",
    [
        "if x:\n    def f(): ...\n",
        "if x:\n    pass\nelse:\n    def f(): ...\n",
        "try:\n    def f(): ...\nexcept E:\n    pass\n",
        "try:\n    pass\nexcept E:\n    def f(): ...\n",
        "try:\n    pass\nexcept E:\n    pass\nelse:\n    def f(): ...\n",
        "try:\n    pass\nfinally:\n    def f(): ...\n",
        "with a:\n    def f(): ...\n",
        "for i in x:\n    def f(): ...\n",
        "for i in x:\n    pass\nelse:\n    def f(): ...\n",
        "while x:\n    def f(): ...\n",
        "while x:\n    pass\nelse:\n    def f(): ...\n",
    ],
    ids=["if", "else", "try", "except", "try-else", "finally", "with", "for", "for-else", "while", "while-else"],
)
def test_a_block_is_looked_through(source) -> None:
    assert _names(source) == ["f"]


def test_a_block_itself_is_not_reported() -> None:
    nodes = collect_definitions(ast.parse("if x:\n    def f(): ...\n").body)
    assert all(isinstance(node, ast.FunctionDef) for node in nodes)


def test_blocks_inside_blocks() -> None:
    source = "if a:\n    try:\n        def f(): ...\n    except E:\n        def g(): ...\n"
    assert _names(source) == ["f", "g"]


def test_definitions_around_a_block_keep_their_order() -> None:
    assert _names("def a(): ...\nif x:\n    def b(): ...\ndef c(): ...\n") == ["a", "b", "c"]


MATCH = "match x:\n    case 1:\n        def f(): ...\n"


def test_a_match_is_looked_through() -> None:
    assert _names(MATCH) == ["f"]


def test_every_case_of_a_match_is_looked_through() -> None:
    source = "match x:\n    case 1:\n        def f(): ...\n    case 2:\n        pass\n    case _:\n        class G: ...\n"
    assert _names(source) == ["f", "G"]


def test_a_try_star_is_looked_through() -> None:
    source = "try:\n    pass\nexcept* E:\n    def f(): ...\n"
    assert _names(source) == ["f"]


def test_a_match_inside_a_block_keeps_the_order() -> None:
    source = "def a(): ...\nif x:\n    match y:\n        case 1:\n            def b(): ...\ndef c(): ...\n"
    assert _names(source) == ["a", "b", "c"]