from src.block import Block
import hashlib
import time

import unittest

class TestBlock(unittest.TestCase):
    def test_block(self):
        index = 0
        previous_hash = "0"
        timestamp = time.time()
        data = "Genesis Block"
        nonce = 0
        block = Block(index, previous_hash, timestamp, data, nonce)
        block_ = Block(index, previous_hash, timestamp, "Genesis block", nonce)

        self.assertEqual(block.index, index)
        self.assertEqual(block.previous_hash, previous_hash)
        self.assertEqual(block.timestamp, timestamp)
        self.assertEqual(block.data, data)
        self.assertEqual(block.nonce, nonce)
        self.assertEqual(block.hash, block.calculate_hash())
        self.assertFalse(block.hash == block_.hash)
        self.assertEqual(block.hash, hashlib.sha256(f"{index}{previous_hash}{timestamp}{data}{nonce}".encode('utf-8')).hexdigest())
        self.assertEqual(str(block), f"Block({index}, {previous_hash}, {timestamp}, {data}, {nonce}, {block.hash})")


if __name__ == '__main__':
    unittest.main()