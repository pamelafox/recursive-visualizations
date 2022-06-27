import pytest

import rcviz


fib_def = """
def fib(n):
  if n == 0:
    return 0
  if n == 1:
    return 1
  else:
    return fib(n - 1) + fib(n - 2)"""


def test_visualize():
    dotgraph = rcviz.visualize(fib_def, "fib(2)")
    print(dotgraph)
    assert "fib(1)" in dotgraph


def test_error_too_many_nodes(monkeypatch):
    monkeypatch.setattr(rcviz, "MAX_FRAMES", 10)

    with pytest.raises(rcviz.TooManyFramesError):
        rcviz.visualize(fib_def, "fib(14)")


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
    dotgraph = rcviz.visualize(rev_def, "rev([1, 2, 3, 4, 5], 0, 4)")
    assert "rev([5, 2, 3, 4, 1], 1, 3)" in dotgraph
    assert "rev([5, 4, 3, 2, 1], 2, 2)" in dotgraph
