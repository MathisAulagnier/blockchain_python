import unittest
from src.blockchain_manager import BlockchainManager

class TestBlockchainManager(unittest.TestCase):
    
    


    def setUp(self):
        # Pour les tests, nous désactivons la création automatique de tokens en passant initial_supply=0 et auto_supply=False.
        self.blockchain_manager = BlockchainManager(difficulty=1, initial_supply=0, origin_wallet="wallet_creator", transaction_threshold=1)
        # Création explicite des wallets qui seront utilisés durant les tests
        self.blockchain_manager.wallet_manager.create_wallet("wallet_creator")
        self.blockchain_manager.wallet_manager.create_wallet("alice")
        self.blockchain_manager.wallet_manager.create_wallet("bob")
        self.blockchain_manager.wallet_manager.create_wallet("creator")
        
    def test_create_initial_supply(self):
        print("Test de la création de l'offre initiale")
        tokens = self.blockchain_manager.create_initial_supply(count=10, origin_wallet="wallet_creator")
        self.assertEqual(len(tokens), 10)
        self.assertEqual(len(self.blockchain_manager.token_manager.tokens), 10, 
                        "Le nombre de tokens dans le gestionnaire doit correspondre au nombre de tokens créés")
        
        
        # Vérifier que le bloc de création a été ajouté (Genesis + création)
        # Selon notre conception, on s'attend normalement à avoir :
        #   Bloc 0 : Genesis block
        #   Bloc 1 : Bloc de création
        # Pourtant, si d'autres opérations (transferts ou commits automatiques)
        # ont été effectuées, un ou plusieurs blocs supplémentaires peuvent être présents.
        self.assertEqual(len(self.blockchain_manager.chain), 2)
        last_block = self.blockchain_manager.get_last_block()
        self.assertEqual(last_block.transactions[0]["action"], "token_creation")
        self.assertEqual(len(last_block.transactions[0]["tokens"]), 10)


    def test_transfer_token(self):
        # Création d'un token avec propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=1, origin_wallet="creator")
        token_id = tokens[0].identifier
        
        # Transfert de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        #self.blockchain_manager.commit_pending_transactions() # Commit automatique après le transfert si jamais le threshold n'est pas atteint or on a mis 1 donc ca le fait d'office
        # Puis mise en staking dans le wallet d'"alice"
        self.blockchain_manager.stake_token(token_id, "alice")
        #self.blockchain_manager.commit_pending_transactions()
        
        # Récupérer l'historique
        history = self.blockchain_manager.get_token_history(token_id)
        print("Historique du token :", history)
        # On attend 3 événements : création, transfert et stake.
        self.assertEqual(len(history), 3)
        
        actions = [event["action"] for event in history]
        self.assertIn("creation", actions)
        self.assertIn("transfer", actions)
        self.assertIn("stake", actions)
        
    def test_stake_token(self):
        # Création d'un token avec propriétaire "alice"
        tokens = self.blockchain_manager.create_initial_supply(count=1, origin_wallet="alice")
        token_id = tokens[0].identifier
        
        alice_wallet = self.blockchain_manager.wallet_manager.get_wallet("alice")
        self.assertNotIn(token_id, alice_wallet.staked_tokens)
        
        # Mise en staking
        self.blockchain_manager.stake_token(token_id, "alice")
        #self.blockchain_manager.commit_pending_transactions()
        self.assertIn(token_id, alice_wallet.staked_tokens)
        
        # Retirer le token du staking
        self.blockchain_manager.unstake_token(token_id, "alice")
        #self.blockchain_manager.commit_pending_transactions()
        self.assertNotIn(token_id, alice_wallet.staked_tokens)
        self.assertIn(token_id, alice_wallet.available_tokens)
        
    def test_get_token_history(self):
        # Création d'un token avec propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=1, origin_wallet="creator")
        token_id = tokens[0].identifier
        
        # Transfert de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        #self.blockchain_manager.commit_pending_transactions()
        # Puis transfert de "alice" vers "bob"
        self.blockchain_manager.transfer_token(token_id, "alice", "bob")
        #self.blockchain_manager.commit_pending_transactions()
        # Et mise en staking dans le wallet de "bob"
        self.blockchain_manager.stake_token(token_id, "bob")
        #self.blockchain_manager.commit_pending_transactions()
        
        history = self.blockchain_manager.get_token_history(token_id)
        # On attend 4 événements : création, transfert (creator->alice), transfert (alice->bob), stake
        self.assertEqual(len(history), 4)
        
        actions = [event["action"] for event in history]
        self.assertIn("creation", actions)
        self.assertIn("transfer", actions)
        self.assertIn("stake", actions)
        
    def test_get_staking_stats(self):
        # Création de 10 tokens avec propriétaire "alice"
        tokens = self.blockchain_manager.create_initial_supply(count=10, origin_wallet="alice")
        stats = self.blockchain_manager.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 0)
        self.assertEqual(stats["staking_percentage"], 0)
        
        # Mettre en staking 3 tokens (indices 0, 2, 4)
        for i in range(0, 6, 2):
            self.blockchain_manager.stake_token(tokens[i].identifier, "alice")
            #self.blockchain_manager.commit_pending_transactions()
            
        stats = self.blockchain_manager.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 3)
        self.assertEqual(stats["staking_percentage"], 30.0)
        
    def test_is_chain_valid(self):
        # Création de 5 tokens avec propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=5, origin_wallet="creator")
        token_id = tokens[0].identifier
        
        # Transfert de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        #self.blockchain_manager.commit_pending_transactions()
        
        self.assertTrue(self.blockchain_manager.is_chain_valid())
        
        # Simuler une modification malveillante du bloc de création
        self.blockchain_manager.chain[1].transactions[0]["action"] = "tampered"
        self.blockchain_manager.chain[1].hash = self.blockchain_manager.chain[1].calculate_hash()
        
        self.assertFalse(self.blockchain_manager.is_chain_valid())

if __name__ == "__main__":
    unittest.main()
