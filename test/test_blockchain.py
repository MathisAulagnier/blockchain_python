import unittest
from src.blockchain import Blockchain, Block
import time

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain()

    def test_initial_chain(self):
        self.assertEqual(len(self.blockchain.chain), 1, 'Initial chain should have only the genesis block')
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].data, ["Genesis Block"])

    def test_add_block(self):
        self.blockchain.add_block(["Transaction 1"])
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.chain[1].index, 1)
        self.assertEqual(self.blockchain.chain[1].data, ["Transaction 1"])

    def test_is_chain_valid(self):
        self.blockchain.add_block(["Transaction 1"])
        self.assertTrue(self.blockchain.is_chain_valid())
        # Tamper with the blockchain
        self.blockchain.chain[1].data = ["Tampered Transaction"]
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_get_last_block(self):
        self.blockchain.add_block(["Transaction 1"])
        last_block = self.blockchain.get_last_block()
        self.assertEqual(last_block.index, 1)
        self.assertEqual(last_block.data, ["Transaction 1"])

    def test_block_hash(self):
        block = Block(0, "0", time.time(), ["Genesis Block"], 0)
        expected_hash = block.calculate_hash()
        self.assertEqual(block.hash, expected_hash)

    def test_blockchain_length(self):
        self.blockchain.add_block(["Transaction 1"])
        self.blockchain.add_block(["Transaction 2"])
        self.assertEqual(len(self.blockchain.chain), 3)


if __name__ == '__main__':
    unittest.main()

       