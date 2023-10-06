import unittest

from hijiki.hijiki import add


class TestMyModule(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)