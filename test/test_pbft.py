#!/usr/bin/env python3
"""
Fichier : test_pbft.py
Ce test unitaire vérifie le bon fonctionnement de la classe PBFTConsensus.
Il teste les différentes phases du consensus PBFT :
- La phase Pre-prepare
- La phase Prepare suivie de la phase Commit avec un consensus réussi
- Un scénario où le consensus échoue en raison d'un nombre insuffisant de votes favorables
"""

import time
import unittest
from src.block import Block
from src.pbft import PBFTConsensus

class TestPBFTConsensus(unittest.TestCase):
    def setUp(self):
        self.validators = ["Alice", "Bob", "Charlie", "David"]
        self.pbft = PBFTConsensus(self.validators)
        # Création d'un bloc de test avec timestamp fixe
        self.block = Block(1, "previous_hash_dummy", ["Dummy transaction"], 1234567890.0)

    def test_pre_prepare(self):
        leader = "Alice"
        msg = self.pbft.pre_prepare(self.block, leader)
        expected_msg = f"Pre-prepare: Bloc {self.block.index} proposé par le leader {leader}"
        self.assertEqual(msg, expected_msg)
        # Vérifie que la phase pre-prepare stocke correctement le message
        self.assertIn(self.block.index, self.pbft.pre_prepare_messages)
        self.assertEqual(self.pbft.pre_prepare_messages[self.block.index]["leader"], leader)

    def test_prepare_and_commit(self):
        # Tous les validateurs votent positivement
        for validator in self.validators:
            self.pbft.prepare(self.block, validator, True)
        # La phase commit doit aboutir
        success, commit_msg = self.pbft.commit(self.block)
        self.assertTrue(success)
        self.assertIn(f"{len(self.validators)}", commit_msg)
        # Vérification de la signature PBFT générée
        expected_signature = f"PBFT_Signature_Block_{self.block.index}"
        self.assertEqual(self.pbft.get_consensus_signature(self.block), expected_signature)

    def test_commit_insufficient_votes(self):
        # Seuls deux validateurs votent positivement
        self.pbft.prepare(self.block, "Alice", True)
        self.pbft.prepare(self.block, "Bob", True)
        success, commit_msg = self.pbft.commit(self.block)
        self.assertFalse(success)
        self.assertIn("rejeté", commit_msg)

if __name__ == '__main__':
    unittest.main()
