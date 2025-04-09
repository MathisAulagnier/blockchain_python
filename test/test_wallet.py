import unittest
from src.wallet import Wallet

class TestWallet(unittest.TestCase):
    def setUp(self):
        # On crée un wallet avec une adresse fixe pour les tests
        self.wallet = Wallet("test_wallet")
        self.token1 = "token1"
        self.token2 = "token2"

    def test_initialization(self):
        # Vérifie que l'adresse est définie et que les ensembles sont vides
        self.assertEqual(self.wallet.address, "test_wallet")
        self.assertEqual(len(self.wallet.available_tokens), 0)
        self.assertEqual(len(self.wallet.staked_tokens), 0)

    def test_deposit_token_available(self):
        # Déposer un token sans staking
        self.wallet.deposit_token(self.token1, stake=False)
        self.assertIn(self.token1, self.wallet.available_tokens)
        self.assertNotIn(self.token1, self.wallet.staked_tokens)

    def test_deposit_token_staked(self):
        # Déposer un token en mode staking
        self.wallet.deposit_token(self.token2, stake=True)
        self.assertIn(self.token2, self.wallet.staked_tokens)
        self.assertNotIn(self.token2, self.wallet.available_tokens)

    def test_withdraw_token(self):
        # Ajouter un token dans available_tokens puis le retirer
        self.wallet.deposit_token(self.token1, stake=False)
        withdrawn = self.wallet.withdraw_token(self.token1)
        self.assertTrue(withdrawn)
        self.assertNotIn(self.token1, self.wallet.available_tokens)
        # Essayer de retirer un token inexistant doit renvoyer False
        withdrawn = self.wallet.withdraw_token("inexistant")
        self.assertFalse(withdrawn)

    def test_stake_token(self):
        # Déposer un token dans available_tokens et le staker
        self.wallet.deposit_token(self.token1, stake=False)
        staked = self.wallet.stake_token(self.token1)
        self.assertTrue(staked)
        self.assertNotIn(self.token1, self.wallet.available_tokens)
        self.assertIn(self.token1, self.wallet.staked_tokens)
        # Tenter de staker un token qui n'existe pas doit renvoyer False
        staked = self.wallet.stake_token("inexistant")
        self.assertFalse(staked)

    def test_unstake_token(self):
        # Déposer un token en staking et le retirer du staking
        self.wallet.deposit_token(self.token1, stake=True)
        unstaked = self.wallet.unstake_token(self.token1)
        self.assertTrue(unstaked)
        self.assertIn(self.token1, self.wallet.available_tokens)
        self.assertNotIn(self.token1, self.wallet.staked_tokens)
        # Essayer de désactiver le staking d'un token inexistant
        unstaked = self.wallet.unstake_token("inexistant")
        self.assertFalse(unstaked)

    def test_balance_methods(self):
        # Vérifier les fonctions balance, staked_balance et total_balance
        self.assertEqual(self.wallet.balance(), 0)
        self.assertEqual(self.wallet.staked_balance(), 0)
        self.assertEqual(self.wallet.total_balance(), 0)
        
        self.wallet.deposit_token(self.token1, stake=False)
        self.wallet.deposit_token(self.token2, stake=True)
        self.assertEqual(self.wallet.balance(), 1)
        self.assertEqual(self.wallet.staked_balance(), 1)
        self.assertEqual(self.wallet.total_balance(), 2)

    def test_repr(self):
        # Vérifier que __repr__ retourne une chaîne comportant les infos attendues
        self.wallet.deposit_token(self.token1, stake=False)
        self.wallet.deposit_token(self.token2, stake=True)
        representation = repr(self.wallet)
        self.assertIn("Wallet(", representation)
        self.assertIn("available: 1", representation)
        self.assertIn("staked: 1", representation)

if __name__ == "__main__":
    unittest.main()
