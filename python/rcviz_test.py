import pytest
import pydot

import rcviz


virfib_def = """
def virfib(n):
  if n == 0:
    return 0
  if n == 1:
    return 1
  else:
    return virfib(n - 1) + virfib(n - 2)"""


def test_visualize():
    dotgraph_str = rcviz.visualize(virfib_def, "virfib(3)")
    dotgraph = pydot.graph_from_dot_data(dotgraph_str)[0]

    assert len(dotgraph.get_nodes()) == 6
    assert len(dotgraph.get_edges()) == 9
    assert [n.get_label() for n in dotgraph.get_nodes()] == [
        '"virfib(3)"',
        '"virfib(2)"',
        '"virfib(1)"',
        '"virfib(0)"',
        '"virfib(1)"',
        "Result",
    ]
    assert [e.get_label() for e in dotgraph.get_edges()] == [
        '"(#1)"',
        '"1 (#6)"',
        '"(#7)"',
        '"1 (#8)"',
        '"(#2)"',
        '"1 (#3)"',
        '"(#4)"',
        '"0 (#5)"',
        '"2 (#9)"',
    ]


def test_error_too_many_nodes(monkeypatch):
    monkeypatch.setattr(rcviz, "MAX_FRAMES", 10)

    with pytest.raises(rcviz.TooManyFramesError):
        rcviz.visualize(virfib_def, "virfib(14)")


def test_error_too_much_time(monkeypatch):
    while_def = """
def inf():
  while True:
    inf()
"""
    monkeypatch.setattr(rcviz, "MAX_TIME", 2)

    with pytest.raises(rcviz.TooMuchTimeError):
        rcviz.visualize(while_def, "inf()")


def test_mutable_args():
    rev_def = """
def rev(lst, start, end):
  if start < end:
    tmp = lst[end]
    lst[end] = lst[start]
    lst[start] = tmp
    rev(lst, start+1, end-1)
"""
    dotgraph_str = rcviz.visualize(rev_def, "rev([1, 2, 3, 4, 5], 0, 4)")
    dotgraph = pydot.graph_from_dot_data(dotgraph_str)[0]

    assert len(dotgraph.get_nodes()) == 3
    assert len(dotgraph.get_edges()) == 2
    assert [n.get_label() for n in dotgraph.get_nodes()] == [
        '"rev([1, 2, 3, 4, 5], 0, 4)"',
        '"rev([5, 2, 3, 4, 1], 1, 3)"',
        '"rev([5, 4, 3, 2, 1], 2, 2)"',
    ]
    assert [e.get_label() for e in dotgraph.get_edges()] == ['"(#1)"', '"(#2)"']


def test_dict_args():
    # Ensure that curly braces get escaped, since curly braces have meaning in dot graphs.

    dict_def = """
def finditem(obj, key):
    if key in obj:
      return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = finditem(v, key)
            if item is not None:
                return item
    """

    dotgraph_str = rcviz.visualize(dict_def, "finditem({'B':1,'A': {'C': 2}},'C')")
    dotgraph = pydot.graph_from_dot_data(dotgraph_str)[0]

    assert [n.get_label() for n in dotgraph.get_nodes()] == [
        "\"finditem(\\{'B': 1, 'A': \\{'C': 2\\}\\}, C)\"",
        "\"finditem(\\{'C': 2\\}, C)\"",
        "Result",
    ]
