import hashlib
import json
import time
import unittest
from src.block import Block

class TestBlock(unittest.TestCase):
    def test_block_properties(self):
        # Utilisation d'une timestamp fixe pour pouvoir comparer
        index = 0
        previous_hash = "0"
        transactions = ["Genesis Block"]
        fixed_time = 1234567890.0

        block = Block(index, previous_hash, transactions, fixed_time)

        # Vérifie que les attributs sont correctement initialisés
        self.assertEqual(block.index, index)
        self.assertEqual(block.previous_hash, previous_hash)
        self.assertEqual(block.transactions, transactions)
        self.assertEqual(block.timestamp, fixed_time)
        self.assertIsNone(block.validator)
        self.assertIsNone(block.pbft_signature)

        # Vérifie que le hash est correctement calculé
        expected_data = {
            "index": index,
            "timestamp": fixed_time,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "validator": None,
            "pbft_signature": None
        }
        expected_hash = hashlib.sha256(json.dumps(expected_data, sort_keys=True).encode()).hexdigest()
        self.assertEqual(block.hash, expected_hash)
        self.assertEqual(block.hash, block.calculate_hash())

    def test_hash_difference_with_different_transactions(self):
        index = 1
        previous_hash = "abc123"
        fixed_time = 1234567890.0
        transactions1 = ["Transaction A"]
        transactions2 = ["Transaction B"]

        block1 = Block(index, previous_hash, transactions1, fixed_time)
        block2 = Block(index, previous_hash, transactions2, fixed_time)

        self.assertNotEqual(block1.hash, block2.hash)

    def test_repr(self):
        index = 2
        previous_hash = "def456"
        transactions = ["Test Transaction"]
        fixed_time = 1234567890.0

        block = Block(index, previous_hash, transactions, fixed_time)
        expected_repr = f"Block({index}, {previous_hash}, {fixed_time}, {transactions}, {block.hash})"
        self.assertEqual(repr(block), expected_repr)

if __name__ == '__main__':
    unittest.main()
