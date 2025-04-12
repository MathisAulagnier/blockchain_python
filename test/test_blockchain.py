#!/usr/bin/env python3
"""
Fichier : test_blockchain.py
Ce test unitaire vérifie le bon fonctionnement de la classe Blockchain.
Les tests portent sur :
- La création du bloc génésis
- L'ajout de transactions et l'enregistrement de validateurs
- L'ajout d'un bloc (avec intégration des données PoS et PBFT)
- La validité de l'intégrité de la chaîne (is_chain_valid)
"""

import time
import unittest
from src.block import Block
from src.blockchain import Blockchain

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_initial_chain(self):
        self.assertEqual(len(self.blockchain.chain), 1, "La chaîne initiale doit comporter uniquement le bloc génésis")
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].transactions, ["Genesis Block"])

    def test_add_block(self):
        self.blockchain.add_transaction("Transaction 1")
        self.blockchain.add_block( "Alice", "PBFT_Signature_1")
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.chain[1].index, 1)
        self.assertEqual(self.blockchain.chain[1].transactions, ["Transaction 1"])

    def test_is_chain_valid(self):
        #print block 1 of the chain 
        self.blockchain.add_transaction("Transaction 1")
        self.blockchain.add_block("Alice", "PBFT_Signature_1")
        self.assertTrue(self.blockchain.is_chain_valid())
        # Altération du bloc pour simuler une corruption
        self.blockchain.chain[1].transactions = ["Tampered Transaction"]
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_get_last_block(self):
        self.blockchain.add_transaction("Transaction 1")
        self.blockchain.add_block("Alice", "PBFT_Signature_1")
        last_block = self.blockchain.get_last_block()
        self.assertEqual(last_block.index, 1)
        self.assertEqual(last_block.transactions, ["Transaction 1"])

    def test_blockchain_length(self):
        self.blockchain.add_transaction("Transaction 1")
        self.blockchain.add_transaction("Transaction 2")
        self.blockchain.add_block( "Alice", "PBFT_Signature_1")
        self.blockchain.add_block("Bob", "PBFT_Signature_2")
        self.assertEqual(len(self.blockchain.chain), 3)

if __name__ == '__main__':
    unittest.main()
