from src.indexation import get_value
import unittest

class TestIndexation(unittest.TestCase):
    def test_get_value(self):
        value = get_value()
        self.assertIsInstance(value, float)
        self.assertIsNotNone(value)
