from src.blockchain import Blockchain, Block

import unittest
import time

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain(difficulty=2)

    def test_initial_chain(self):
        self.assertEqual(len(self.blockchain.chain), 1, 'Initial chain should have only the genesis block')
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].transactions, ["Genesis Block"])

    def test_add_block(self):
        self.blockchain.add_block(["Transaction 1"])
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.chain[1].index, 1)
        self.assertEqual(self.blockchain.chain[1].transactions, ["Transaction 1"])

    def test_is_chain_valid(self):
        self.blockchain.add_block(["Transaction 1"])
        self.assertTrue(self.blockchain.is_chain_valid())
        # Tamper with the blockchain
        self.blockchain.chain[1].transactions = ["Tampered Transaction"]
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_get_last_block(self):
        self.blockchain.add_block(["Transaction 1"])
        last_block = self.blockchain.get_last_block()
        self.assertEqual(last_block.index, 1)
        self.assertEqual(last_block.transactions, ["Transaction 1"])

    def test_blockchain_length(self):
        self.blockchain.add_block(["Transaction 1"])
        self.blockchain.add_block(["Transaction 2"])
        self.assertEqual(len(self.blockchain.chain), 3)


if __name__ == '__main__':
    unittest.main()

       