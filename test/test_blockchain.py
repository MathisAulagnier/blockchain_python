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

    def test_genesis_block(self):
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(genesis.transactions, ["Genesis Block"])

    def test_add_action_and_block(self):
        # Ajout d'une transaction
        tx = "Alice envoie 1 token à Bob"
        self.blockchain.add_action(tx)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
        
        # Enregistrement d'un validateur
        self.blockchain.register_validator("Validator1", 100)
        self.assertIn("Validator1", self.blockchain.validators)
        self.assertEqual(self.blockchain.stakes["Validator1"], 100)

        # Choix du validateur (ici, seul enregistré)
        chosen_validator = self.blockchain.choose_validator()
        self.assertEqual(chosen_validator, "Validator1")

        # Ajout d'un bloc avec une signature PBFT fictive
        dummy_signature = "dummy_signature"
        self.blockchain.add_block(chosen_validator, dummy_signature)
        
        # Après ajout, les transactions en attente doivent être vidées et la chaîne comporter 2 blocs
        self.assertEqual(len(self.blockchain.pending_transactions), 0)
        self.assertEqual(len(self.blockchain.chain), 2)
        
        new_block = self.blockchain.chain[1]
        self.assertEqual(new_block.validator, "Validator1")
        self.assertEqual(new_block.pbft_signature, dummy_signature)
        # Vérifie que le bloc référence bien le hash du bloc précédent
        self.assertEqual(new_block.previous_hash, self.blockchain.chain[0].hash)

    def test_is_chain_valid(self):
        # Ajoute une transaction et un bloc correct
        self.blockchain.add_action("Test Transaction")
        self.blockchain.register_validator("Validator1", 50)
        chosen_validator = self.blockchain.choose_validator()
        self.blockchain.add_block(chosen_validator, "sig")
        self.assertTrue(self.blockchain.is_chain_valid())

        # Altération d'un bloc pour simuler une corruption
        self.blockchain.chain[1].transactions = ["Tampered Transaction"]
        self.assertFalse(self.blockchain.is_chain_valid())

if __name__ == '__main__':
    unittest.main()
