#!/usr/bin/env python3
"""
Fichier : test_pbft.py
Ce test unitaire vérifie le bon fonctionnement de la classe PBFT.
Il teste les différentes phases du consensus PBFT :
- La phase Pre-prepare
- La phase Prepare suivie de la phase Commit avec un consensus réussi
- Le cas d'un consensus échoué en raison d'un nombre insuffisant de votes favorables pondérés par le stake.
"""

import unittest
from src.block import Block
from src.pbft import PBFT

class TestPBFTConsensus(unittest.TestCase):
    def setUp(self):
        # Définition des validateurs et de leur stake respectif.
        self.validators = ["Alice", "Bob", "Charlie", "David"]
        self.stakes = {
            "Alice": 10,
            "Bob": 20,
            "Charlie": 30,
            "David": 40
        }
        
        # Instanciation de la classe PBFT avec les validateurs et leurs stakes.
        self.pbft = PBFT(self.validators, self.stakes)
        # Création d'un bloc de test avec un timestamp fixe.
        self.block = Block(
            index=1,
            previous_hash="previous_hash_dummy",
            transactions=["Dummy transaction"],
            timestamp=1234567890.0
        )

    def test_pre_prepare(self):
        """Teste la phase Pre-prepare qui enregistre le bloc et le leader associé."""
        leader = "Alice"
        msg = self.pbft.pre_prepare(self.block, leader)
        expected_msg = f"Pre-prepare: Bloc {self.block.index} proposé par le leader {leader}"
        self.assertEqual(msg, expected_msg, "Le message de pre-prepare n'est pas celui attendu.")
        
        # Vérifie que le message a bien été stocké dans le dictionnaire.
        self.assertIn(self.block.index, self.pbft.pre_prepare_messages,
                      "Le bloc candidat n'est pas présent dans le dictionnaire pre_prepare_messages.")
        self.assertEqual(self.pbft.pre_prepare_messages[self.block.index]["leader"], leader,
                         "Le leader stocké n'est pas celui attendu.")

    def test_prepare_and_commit(self):
        """Teste le cas où tous les validateurs votent positivement, menant à un consensus réussi."""
        # Chaque validateur vote positivement sur le bloc.
        for validator in self.validators:
            self.pbft.prepare(self.block, validator, True)
        
        # La phase Commit doit ensuite valider le bloc.
        success, commit_msg = self.pbft.commit(self.block)
        self.assertTrue(success, "Le bloc devrait être validé lorsque tous les votes sont positifs.")
        
        # Vérification de la signature de consensus générée.
        expected_signature = f"PBFT_Signature_Block_{self.block.index}"
        self.assertEqual(self.pbft.get_consensus_signature(self.block), expected_signature,
                         "La signature de consensus générée n'est pas celle attendue.")

    def test_commit_insufficient_votes(self):
        """Teste le cas où un nombre insuffisant de votes positifs conduit à un rejet du bloc."""
        # Seuls deux validateurs votent positivement.
        self.pbft.prepare(self.block, "Alice", False)
        self.pbft.prepare(self.block, "Bob", False)
        
        # La phase Commit doit échouer : la somme pondérée des votes favorables n'atteint pas 2/3 du total.
        success, commit_msg = self.pbft.commit(self.block)
        self.assertFalse(success)
        self.assertIn("rejeté", commit_msg, "Le message de commit doit indiquer que le bloc est rejeté.")

if __name__ == '__main__':
    unittest.main()
