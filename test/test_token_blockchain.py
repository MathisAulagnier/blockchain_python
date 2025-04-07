import unittest
from src.token_blockchain import TokenBlockchain

class TestTokenBlockchain(unittest.TestCase):
    def setUp(self):
        self.token_blockchain = TokenBlockchain(difficulty=1)  # Difficulté réduite pour les tests
        
    def test_create_initial_supply(self):
        tokens = self.token_blockchain.create_initial_supply(count=10)
        self.assertEqual(len(tokens), 10)
        self.assertEqual(len(self.token_blockchain.token_manager.tokens), 10, "Le nombre de tokens dans le gestionnaire doit correspondre au nombre de tokens créés")
        
        # Vérifier que le bloc de création a été ajouté
        self.assertEqual(len(self.token_blockchain.chain), 2)  # Genesis block + création
        last_block = self.token_blockchain.get_last_block()
        # print(last_block.transactions["action"])
        self.assertEqual(last_block.transactions["action"], "token_creation")
        self.assertEqual(len(last_block.transactions["tokens"]), 10)
        
    def test_transfer_token(self):
        # Créer un token
        tokens = self.token_blockchain.create_initial_supply(count=1)
        token_id = tokens[0].identifier
        
        # Effectuer un transfert
        tx = self.token_blockchain.transfer_token(token_id, "alice", "bob")
        
        # Vérifier que la transaction a été enregistrée
        self.assertEqual(tx["action"], "transfer")
        self.assertEqual(tx["token_id"], token_id)
        self.assertEqual(tx["from"], "alice")
        self.assertEqual(tx["to"], "bob")
        
        # Vérifier que le bloc a été ajouté
        self.assertEqual(len(self.token_blockchain.chain), 3)  # Genesis + création + transfert
        
    def test_stake_token(self):
        # Créer un token
        tokens = self.token_blockchain.create_initial_supply(count=1)
        token_id = tokens[0].identifier
        
        # Le token ne devrait pas être en staking initialement
        self.assertFalse(tokens[0].staking)
        
        # Mettre le token en staking
        tx = self.token_blockchain.stake_token(token_id, "alice")
        
        # Vérifier que le token est maintenant en staking
        self.assertTrue(tokens[0].staking)
        self.assertEqual(tx["action"], "stake")
        
        # Retirer le token du staking
        tx = self.token_blockchain.stake_token(token_id, "alice")
        
        # Vérifier que le token n'est plus en staking
        self.assertFalse(tokens[0].staking)
        self.assertEqual(tx["action"], "unstake")
        
    def test_get_token_history(self):
        # Créer un token
        tokens = self.token_blockchain.create_initial_supply(count=1)
        token_id = tokens[0].identifier
        
        # Effectuer quelques transactions
        self.token_blockchain.transfer_token(token_id, "creator", "alice")
        self.token_blockchain.transfer_token(token_id, "alice", "bob")
        self.token_blockchain.stake_token(token_id, "bob")
        
        # Récupérer l'historique
        history = self.token_blockchain.get_token_history(token_id)
        print(history)
        
        # On devrait avoir 4 événements: création, 2 transferts, 1 stake
        self.assertEqual(len(history), 3)
        
        # Vérifier que les actions sont correctes
        actions = [event["action"] for event in history]
        self.assertIn("transfer", actions)
        self.assertIn("stake", actions)
        
    def test_get_staking_stats(self):
        # Créer des tokens
        tokens = self.token_blockchain.create_initial_supply(count=10)
        
        # Aucun token en staking initialement
        stats = self.token_blockchain.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 0)
        self.assertEqual(stats["staking_percentage"], 0)
        
        # Mettre quelques tokens en staking
        for i in range(0, 6, 2):  # 3 tokens
            self.token_blockchain.stake_token(tokens[i].identifier, "alice")
            
        # Vérifier les nouvelles statistiques
        stats = self.token_blockchain.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 3)
        self.assertEqual(stats["staking_percentage"], 30.0)
        
    def test_is_chain_valid(self):
        # Créer quelques tokens et effectuer des transactions
        tokens = self.token_blockchain.create_initial_supply(count=5)
        token_id = tokens[0].identifier
        self.token_blockchain.transfer_token(token_id, "creator", "alice")
        
        # La chaîne devrait être valide
        self.assertTrue(self.token_blockchain.is_chain_valid())
        
        # Tenter de modifier un bloc pour rendre la chaîne invalide
        self.token_blockchain.chain[1].transactions["action"] = "tampered"
        
        # Recalculer le hash pour simuler une modification malveillante
        # (Dans un cas réel, le hash ne correspondrait plus)
        self.token_blockchain.chain[1].hash = self.token_blockchain.chain[1].calculate_hash()
        
        # La chaîne devrait maintenant être invalide car le hash a changé
        self.assertFalse(self.token_blockchain.is_chain_valid())

