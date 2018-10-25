import unittest

from chasm.chasm import make_sum


class ChasmUnittests(unittest.TestCase):
    def test_sum(self):
        assert make_sum(6, 9) == 6 + 9