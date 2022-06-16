import unittest

from rcviz import visualize, TooManyFramesError, TooMuchTimeError


class TestRCViz(unittest.TestCase):

    fib_def = """
def fib(n):
  if n == 0:
    return 0
  if n == 1:
    return 1
  else:
    return fib(n - 1) + fib(n - 2)"""

    def test_svg(self):
        dotgraph = visualize(self.fib_def, "fib(2)")
        self.assertIn("fib(1)", dotgraph)

    def test_mutable_args(self):
        rev_def = """
def rev(lst, start, end):
  if start < end:
    tmp = lst[end]
    lst[end] = lst[start]
    lst[start] = tmp
    rev(lst, start+1, end-1)
"""
        dotgraph = visualize(rev_def, "rev([1, 2, 3, 4, 5], 0, 4)")
        self.assertIn("rev([5, 2, 3, 4, 1], 1, 3)", dotgraph)
        self.assertIn("rev([5, 4, 3, 2, 1], 2, 2)", dotgraph)

    def test_error_too_many_nodes(self):
        with self.assertRaises(TooManyFramesError):
            visualize(self.fib_def, "fib(14)")

    def test_error_too_much_time(self):
        while_def = """
def inf():
  while True:
    inf()
"""
        with self.assertRaises(TooMuchTimeError):
            visualize(while_def, "inf()")


if __name__ == "__main__":
    unittest.main()
