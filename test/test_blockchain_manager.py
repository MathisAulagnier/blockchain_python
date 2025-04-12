import unittest
import time
from src.blockchain_manager import BlockchainManager

class TestBlockchainManager(unittest.TestCase):
    def setUp(self):
        # Initialisation avec 100 tokens (les trois wallets de base seront alimentés automatiquement)
        self.blockchain = BlockchainManager(initial_supply=100, transaction_threshold=1)
        # Récupération de la liste complète de tokens (pour information)
        self.tokens = self.blockchain.token_manager.get_all_tokens()
        
    def get_origin_token(self):
        """Retourne l'identifiant d'un token disponible dans wallet_creator."""
        origin_wallet = self.blockchain.wallet_manager.get_wallet("wallet_creator")
        if not origin_wallet.available_tokens:
            self.fail("Aucun token disponible dans wallet_creator.")
        # Conversion du set en liste pour accéder au premier élément
        return list(origin_wallet.available_tokens)[0]


    def test_is_chain_valid(self):
        # Récupérer deux tokens disponibles dans wallet_creator
        token_id = self.get_origin_token()
        #get second origin token        
        self.blockchain.transfer_token(token_id, "wallet_creator", "wallet_JJ")
        token_id_extra = self.get_origin_token()  # Un autre token disponible après le premier transfert
        self.blockchain.transfer_token(token_id_extra, "wallet_creator", "wallet_Lina")
        # Vérifie que la chaîne est valide

        self.assertTrue(self.blockchain.is_chain_valid())
        
        # Altération manuelle d'une transaction (dans un bloc autre que le bloc d'initialisation)
        if len(self.blockchain.chain) > 1:
            # Modification de la première transaction du deuxième bloc pour simuler une altération
            self.blockchain.chain[1].transactions[0]["from"] = "hacker"
            # Recalcule du hash du bloc altéré
            self.blockchain.chain[1].hash = self.blockchain.chain[1].calculate_hash()
            self.assertFalse(self.blockchain.is_chain_valid())
        else:
            self.skipTest("Pas assez de blocs pour tester l'altération.")

if __name__ == '__main__':
    unittest.main()
