# wallet.py
import uuid

class Wallet:
    def __init__(self, address=None):
        self.address = address or str(uuid.uuid4()) # Si une adresse est fournie, on l'utilise, sinon on en génère une unique.
        self.available_tokens = set()
        self.staked_tokens = set()
    
    def deposit_token(self, token_id, stake=False):
        """Ajoute un token dans le wallet.
           Si stake=True, le token est déposé dans le solde staké.
        """
        if stake:
            self.staked_tokens.add(token_id)
        else:
            self.available_tokens.add(token_id)
    
    def withdraw_token(self, token_id):
        """Retire un token du solde disponible (pour un transfert par exemple)."""
        if token_id in self.available_tokens:
            self.available_tokens.remove(token_id)
            return True
        return False

    def stake_token(self, token_id):
        """Déplace un token du solde disponible vers le solde staké."""
        if token_id in self.available_tokens:
            self.available_tokens.remove(token_id)
            self.staked_tokens.add(token_id)
            return True
        return False

    def unstake_token(self, token_id):
        """Déplace un token du solde staké vers le solde disponible."""
        if token_id in self.staked_tokens:
            self.staked_tokens.remove(token_id)
            self.available_tokens.add(token_id)
            return True
        return False

    def balance(self):
        return len(self.available_tokens)

    def staked_balance(self):
        return len(self.staked_tokens)

    def total_balance(self):
        return self.balance() + self.staked_balance()

    def __repr__(self):
        return f"Wallet({self.address}, available: {self.balance()}, staked: {self.staked_balance()})"
