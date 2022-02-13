import unittest

from rcviz import visualize, TooManyFramesError, TooMuchTimeError

class TestRCViz(unittest.TestCase):

  fib_def = """
@viz
def fib(n):
  if n == 0:
    return 0
  if n == 1:
    return 1
  else:
    return fib(n - 1) + fib(n - 2)"""

  def test_svg(self):
    svg = visualize(self.fib_def, 'fib(2)')
    self.assertIn('fib(1)', svg)

  def test_error_too_many_nodes(self):
    with self.assertRaises(TooManyFramesError):
      visualize(self.fib_def, 'fib(14)')

  def test_error_too_much_time(self):
    while_def = """
@viz
def inf():
  while True:
    inf()
"""
    with self.assertRaises(TooMuchTimeError):
      visualize(while_def, 'inf()')

if __name__ == '__main__':
    unittest.main()
