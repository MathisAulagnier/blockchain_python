from src.block import Block
import hashlib
import time
import json
import unittest

class TestBlock(unittest.TestCase):
    def test_block(self):
        index = 0
        previous_hash = "0"
        transactions = ["Genesis Block"]
        difficulty = 2

        t = time.time()

        block = Block(index, previous_hash, transactions, difficulty, t)
        block_ = Block(index, previous_hash, ["Genesis block"], difficulty, t)

        self.assertEqual(block.index, index)
        self.assertEqual(block.previous_hash, previous_hash)
        self.assertEqual(block.transactions, transactions)
        self.assertEqual(block.hash, block.calculate_hash())
        self.assertFalse(block.hash == block_.hash)
        self.assertEqual(
            block.hash,hashlib.sha256(json.dumps({
                "index": index,
                "timestamp": t,
                "transactions": transactions,
                "previous_hash": previous_hash,
                "nonce": block.nonce
            }, sort_keys=True).encode()).hexdigest())
        self.assertEqual(str(block), f"Block({index}, {previous_hash}, {t}, {transactions}, {block.nonce}, {block.hash})")


if __name__ == '__main__':
    unittest.main()