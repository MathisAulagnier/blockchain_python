import unittest
import time
from src.blockchain_manager import BlockchainManager

class TestBlockchainManager(unittest.TestCase):
    def setUp(self):
        # Initialisation sans auto-commit (seuil élevé)
        self.blockchain = BlockchainManager(initial_supply=100, transaction_threshold=10)
        # Origin wallet exists and validators have been registered from initial supply
        self.origin = self.blockchain.wallet_manager.get_wallet("wallet_creator")
        self.validators = list(self.blockchain.validators)

    def get_origin_token(self):
        if not self.origin.available_tokens:
            self.fail("Aucun token disponible dans wallet_creator.")
        return list(self.origin.available_tokens)[0]

    def test_valid_chain_after_transfers(self):
        # Transfert réussi doit donner une chaîne valide
        token = self.get_origin_token()
        # Assurer votes favorables
        self.blockchain.manual_votes = {v: True for v in self.validators}
        self.blockchain.transfer_token(token, "wallet_creator", "wallet_JJ")
        # Appel explicite au commit
        self.blockchain.commit_pending_transactions()
        # La chaîne doit rester valide
        self.assertTrue(self.blockchain.is_chain_valid())
        # Token doit être dans wallet_JJ
        jj = self.blockchain.wallet_manager.get_wallet("wallet_JJ")
        self.assertIn(token, jj.available_tokens)
        self.assertNotIn(token, self.origin.available_tokens)

    def test_transfer_rollback_on_consensus_failure(self):
        token = self.get_origin_token()
        # Forcer votes négatifs -> échec
        self.blockchain.manual_votes = {v: False for v in self.validators}
        self.blockchain.transfer_token(token, "wallet_creator", "wallet_JJ")
        # Après transfert local, token n'est plus dans origin
        self.assertNotIn(token, self.origin.available_tokens)
        # Commit et rollback
        self.blockchain.commit_pending_transactions()
        # Rollback doit avoir remis le token dans origin
        self.assertIn(token, self.origin.available_tokens)
        # Et pas dans wallet_JJ
        jj = self.blockchain.wallet_manager.get_wallet("wallet_JJ")
        self.assertNotIn(token, jj.available_tokens)
        # Pending lists vidées
        self.assertEqual(self.blockchain.pending_transactions, [])
        self.assertEqual(self.blockchain.pending_rollbacks, [])

    def test_stake_and_unstake_rollback(self):
        # Choisir un token de testing
        token = self.get_origin_token()
        # Test du staking rollback
        self.blockchain.manual_votes = {v: False for v in self.validators}
        # staking local
        self.blockchain.stake_token(token, "wallet_creator")
        # le token doit être en staked
        self.assertIn(token, self.origin.staked_tokens)
        self.assertNotIn(token, self.origin.available_tokens)
        # commit et rollback
        self.blockchain.commit_pending_transactions()
        # après rollback, disponible
        self.assertIn(token, self.origin.available_tokens)
        self.assertNotIn(token, self.origin.staked_tokens)

        # Test du unstaking rollback
        # d'abord staker un token avec commit réussi
        self.blockchain.manual_votes = {v: True for v in self.validators}
        self.blockchain.stake_token(token, "wallet_creator")
        self.blockchain.commit_pending_transactions()
        # now unstake locally
        self.blockchain.manual_votes = {v: False for v in self.validators}
        self.blockchain.unstake_token(token, "wallet_creator")
        self.assertIn(token, self.origin.available_tokens)
        # commit et rollback
        self.blockchain.commit_pending_transactions()
        # après rollback, token doit être restaké
        self.assertIn(token, self.origin.staked_tokens)
        self.assertNotIn(token, self.origin.available_tokens)

if __name__ == '__main__':
    unittest.main()
