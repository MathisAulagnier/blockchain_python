import time
import unittest
from src.blockchain_pow import BlockchainPow
from src.block_pow import BlockPow

class TestBlockchainPow(unittest.TestCase):

    def setUp(self):
        self.blockchain = BlockchainPow(difficulty=2)

    def test_initial_chain(self):
        self.assertEqual(len(self.blockchain.chain), 1, "La chaîne initiale doit comporter uniquement le bloc génésis")
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
        # Altération du bloc pour simuler une corruption
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
