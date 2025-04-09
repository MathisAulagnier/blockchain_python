import unittest
from src.wallet_manager import WalletManager

class TestWalletManager(unittest.TestCase):
    def setUp(self):
        self.manager = WalletManager()

    def test_create_wallet_with_address(self):
        # On crée un wallet avec une adresse spécifique
        address = "test_wallet"
        wallet = self.manager.create_wallet(address)
        self.assertEqual(wallet.address, address)
        self.assertIn(address, self.manager.wallets)

    def test_create_wallet_without_address(self):
        # On crée un wallet sans adresse fournie ; l'adresse doit être générée automatiquement
        wallet = self.manager.create_wallet()
        self.assertIsNotNone(wallet.address)
        self.assertIn(wallet.address, self.manager.wallets)

    def test_get_wallet_exists(self):
        # Créer un wallet et le récupérer ensuite
        address = "wallet1"
        created_wallet = self.manager.create_wallet(address)
        retrieved_wallet = self.manager.get_wallet(address)
        self.assertEqual(created_wallet, retrieved_wallet)

    def test_get_wallet_not_exists(self):
        # Tenter de récupérer un wallet inexistant doit lever une ValueError
        with self.assertRaises(ValueError) as context:
            self.manager.get_wallet("non_existent_wallet")
        self.assertIn("n'existe pas", str(context.exception))

    def test_deposit_token_available(self):
        # Tester la méthode deposit: dépôt d'un token en mode available (stake=False)
        address = "wallet_deposit"
        self.manager.create_wallet(address)
        token_id = "token_123"
        wallet = self.manager.deposit(address, token_id, stake=False)
        self.assertIn(token_id, wallet.available_tokens)
        self.assertNotIn(token_id, wallet.staked_tokens)

    def test_deposit_token_staked(self):
        # Tester la méthode deposit: dépôt d'un token en mode staké (stake=True)
        address = "wallet_stake"
        self.manager.create_wallet(address)
        token_id = "token_456"
        wallet = self.manager.deposit(address, token_id, stake=True)
        self.assertIn(token_id, wallet.staked_tokens)
        self.assertNotIn(token_id, wallet.available_tokens)

if __name__ == "__main__":
    unittest.main()
