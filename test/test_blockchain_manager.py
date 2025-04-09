import unittest
from src.blockchain_manager import BlockchainManager

class TestBlockchainManager(unittest.TestCase):
    def setUp(self):
        self.blockchain_manager = BlockchainManager(difficulty=1)  # Difficulté réduite pour les tests
        # Créer explicitement les wallets qui seront utilisés durant les tests
        self.blockchain_manager.wallet_manager.create_wallet("wallet_creator")
        self.blockchain_manager.wallet_manager.create_wallet("alice")
        self.blockchain_manager.wallet_manager.create_wallet("bob")
        self.blockchain_manager.wallet_manager.create_wallet("creator")
        
    def test_create_initial_supply(self):
        tokens = self.blockchain_manager.create_initial_supply(count=10)
        self.assertEqual(len(tokens), 10)
        self.assertEqual(len(self.blockchain_manager.token_manager.tokens), 10, "Le nombre de tokens dans le gestionnaire doit correspondre au nombre de tokens créés")
        
        # Vérifier que le bloc de création a été ajouté
        self.assertEqual(len(self.blockchain_manager.chain), 2)  # Genesis block + création
        last_block = self.blockchain_manager.get_last_block()
        # print(last_block.transactions["action"])
        self.assertEqual(last_block.transactions[0]["action"], "token_creation")
        self.assertEqual(len(last_block.transactions[0]["tokens"]), 10)

        
    def test_transfer_token(self):
        # Création d'un token avec propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=1, owner_address="creator")
        token_id = tokens[0].identifier
        
        # Effectuer quelques transactions :
        # Transfert de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        # Et mettre le token en staking dans le wallet de "alice"
        self.blockchain_manager.stake_token(token_id, "alice")
        
        # Récupérer l'historique
        history = self.blockchain_manager.get_token_history(token_id)
        print("Historique du token :", history)
        
        # Selon l'implémentation actuelle, on obtient :
        # - l'événement de création (issu du bloc de création)
        # - l'événement de transfert (creator -> alice)
        # - l'événement de staking
        # Ainsi, on attend 3 événements.
        self.assertEqual(len(history), 3)
        
        actions = [event["action"] for event in history]
        self.assertIn("creation", actions)
        self.assertIn("transfer", actions)
        self.assertIn("stake", actions)
        
    def test_stake_token(self):
        # Créer l'offre avec propriétaire "alice"
        tokens = self.blockchain_manager.create_initial_supply(count=1, owner_address="alice")
        token_id = tokens[0].identifier
        
        # Vérifier que le token n'est pas en staking dans le wallet d'alice au début
        alice_wallet = self.blockchain_manager.wallet_manager.get_wallet("alice")
        self.assertNotIn(token_id, alice_wallet.staked_tokens)
        
        # Mettre le token en staking
        stake_tx = self.blockchain_manager.stake_token(token_id, "alice")
        
        # Vérifier que le token est bien déplacé dans staked_tokens
        self.assertIn(token_id, alice_wallet.staked_tokens)
        self.assertEqual(stake_tx["action"], "stake")
        
        # Retirer le token du staking via la fonction dédiée
        unstake_tx = self.blockchain_manager.unstake_token(token_id, "alice")
        
        # Vérifier que le token a bien été déplacé vers available_tokens
        self.assertNotIn(token_id, alice_wallet.staked_tokens)
        self.assertIn(token_id, alice_wallet.available_tokens)
        self.assertEqual(unstake_tx["action"], "unstake")
        
    def test_get_token_history(self):
        # Création d'un token avec propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=1, owner_address="creator")
        token_id = tokens[0].identifier
        
        # Effectuer quelques transactions :
        # Transfert de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        # Puis transfert de "alice" vers "bob"
        self.blockchain_manager.transfer_token(token_id, "alice", "bob")
        # Et mettre le token en staking dans le wallet de "bob"
        self.blockchain_manager.stake_token(token_id, "bob")
        
        # Récupérer l'historique
        history = self.blockchain_manager.get_token_history(token_id)
        # Selon notre séquence, on devrait obtenir 4 événements : création, transfert (creator->alice), transfert (alice->bob), stake
        self.assertEqual(len(history), 4)
        
        actions = [event["action"] for event in history]
        self.assertIn("creation", actions)
        self.assertIn("transfer", actions)
        self.assertIn("stake", actions)
        
    def test_get_staking_stats(self):
        # Créer des tokens avec le propriétaire "alice"
        tokens = self.blockchain_manager.create_initial_supply(count=10, owner_address="alice")
        
        # Aucun token en staking initialement
        stats = self.blockchain_manager.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 0)
        self.assertEqual(stats["staking_percentage"], 0)
        
        # Mettre quelques tokens en staking : staker 3 tokens
        for i in range(0, 6, 2):  # Indices 0, 2, 4
            self.blockchain_manager.stake_token(tokens[i].identifier, "alice")
            
        stats = self.blockchain_manager.get_staking_stats()
        self.assertEqual(stats["total_tokens"], 10)
        self.assertEqual(stats["staking_tokens"], 3)
        self.assertEqual(stats["staking_percentage"], 30.0)
        
    def test_is_chain_valid(self):
        # Créer des tokens avec le propriétaire "creator"
        tokens = self.blockchain_manager.create_initial_supply(count=5, owner_address="creator")
        token_id = tokens[0].identifier
        
        # Transférer un token de "creator" vers "alice"
        self.blockchain_manager.transfer_token(token_id, "creator", "alice")
        
        # La chaîne devrait être valide
        self.assertTrue(self.blockchain_manager.is_chain_valid())
        
        # Simuler une modification malveillante du bloc de création
        self.blockchain_manager.chain[1].transactions[0]["action"] = "tampered"
        self.blockchain_manager.chain[1].hash = self.blockchain_manager.chain[1].calculate_hash()
        
        # La chaîne devrait maintenant être invalide
        self.assertFalse(self.blockchain_manager.is_chain_valid())

