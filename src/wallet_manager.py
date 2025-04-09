# wallet_manager.py
from src.wallet import Wallet

class WalletManager:
    def __init__(self):
        self.wallets = {}
    
    def create_wallet(self, address=None):
        wallet = Wallet(address)
        self.wallets[wallet.address] = wallet
        return wallet
    
    def get_wallet(self, address):
        if address in self.wallets:
            return self.wallets[address]
        raise ValueError(f"Le wallet '{address}' n'existe pas.")
    
    def deposit(self, address, token_id, stake=False):
        wallet = self.get_wallet(address)
        wallet.deposit_token(token_id, stake)
        return wallet
