import time
from src.blockchain_pow import BlockchainPow as Blockchain
from src.token_manager import TokenManager
from src.wallet_manager import WalletManager

class BlockchainManager(Blockchain):
    def __init__(self, difficulty=2, initial_supply=100, origin_wallet="wallet_creator", transaction_threshold=2):
        super().__init__(difficulty)
        self.token_manager = TokenManager(max_tokens=100)
        self.wallet_manager = WalletManager()
        self.transaction_threshold = transaction_threshold  # Seuil d'automatisme de commit
        self.pending_transactions = []  # Liste des transactions en attente
        self.origin_wallet = origin_wallet
        # Création (ou récupération) du wallet d'origine
        try:
            self.wallet_manager.get_wallet(self.origin_wallet)
        except ValueError:
            self.wallet_manager.create_wallet(self.origin_wallet)
        # Création de l'offre initiale et commit immédiat des transactions de création si token n'est pas à 0
        if initial_supply > 0:
            self.create_initial_supply(count=initial_supply, origin_wallet=self.origin_wallet)
        
    def add_transaction(self, transaction):
        """Ajoute une transaction (ou une liste de transactions) à la file d'attente."""
        if isinstance(transaction, list):
            self.pending_transactions.extend(transaction)
        else:
            self.pending_transactions.append(transaction)
        
        # Vérifier si le nombre de transactions atteint le seuil pour commiter
        if len(self.pending_transactions) >= self.transaction_threshold:
            self.commit_pending_transactions()
            
    def commit_pending_transactions(self):
        """Crée un nouveau bloc avec toutes les transactions en attente et vide la file."""
        if not self.pending_transactions:
            print("Aucune transaction à commiter.")
            return
        self.add_block(self.pending_transactions)
        self.pending_transactions = []
    
    def create_initial_supply(self, count=100, origin_wallet="wallet_creator"):
        """
        Crée l'offre initiale de tokens et les attribue au wallet d'origine.
        La transaction de création est ajoutée aux transactions en attente
        puis committée immédiatement.
        """
        tokens = self.token_manager.create_initial_tokens(count)
        try:
            owner_wallet = self.wallet_manager.get_wallet(origin_wallet)
        except ValueError:
            owner_wallet = self.wallet_manager.create_wallet(origin_wallet)
        for token in tokens:
            owner_wallet.deposit_token(token.identifier, stake=False)
        token_data = [token.to_dict() for token in tokens]
        self.add_transaction([{"action": "token_creation", "owner": origin_wallet, "tokens": token_data}])
        self.commit_pending_transactions()
        return tokens

    def transfer_token(self, token_id, from_address, to_address):
        """
        Transfère un token d'un wallet à un autre et ajoute la transaction en file.
        Le transfert n'est pas immédiatement validé par la création d'un bloc.
        """
        from_wallet = self.wallet_manager.get_wallet(from_address)
        to_wallet = self.wallet_manager.get_wallet(to_address)
        if token_id not in from_wallet.available_tokens:
            raise ValueError(f"Token {token_id} n'est pas disponible dans le wallet {from_address} (peut être en staking)")
        from_wallet.withdraw_token(token_id)
        to_wallet.deposit_token(token_id, stake=False)
        transaction = {
            "action": "transfer",
            "token_id": token_id,
            "from": from_address,
            "to": to_address,
            "timestamp": time.time()
        }
        self.add_transaction(transaction)
        return transaction

    def stake_token(self, token_id, address):
        """
        Déplace un token du solde disponible vers le solde staké dans le wallet spécifié,
        et ajoute la transaction en file.
        """
        wallet = self.wallet_manager.get_wallet(address)
        if token_id not in wallet.available_tokens:
            raise ValueError(f"Token {token_id} n'est pas disponible dans le wallet {address} pour être staké")
        wallet.stake_token(token_id)
        transaction = {
            "action": "stake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_transaction(transaction)
        return transaction

    def unstake_token(self, token_id, address):
        """
        Déplace un token du solde staké vers le solde disponible du wallet spécifié,
        et ajoute la transaction en file.
        """
        wallet = self.wallet_manager.get_wallet(address)
        if token_id not in wallet.staked_tokens:
            raise ValueError(f"Token {token_id} n'est pas en staking dans le wallet {address}")
        wallet.unstake_token(token_id)
        transaction = {
            "action": "unstake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_transaction(transaction)
        return transaction

    def get_token_history(self, token_id):
        """Retourne l'historique des transactions pour un token spécifique."""
        token_transactions = []
        for block in self.chain:
            for transaction in block.transactions:
                # Si la transaction individuelle concerne ce token
                if isinstance(transaction, dict) and transaction.get("token_id") == token_id:
                    t = transaction.copy()
                    t["block_hash"] = block.hash
                    t["block_index"] = block.index
                    token_transactions.append(t)
                # Pour une transaction groupée de création
                elif (isinstance(transaction, dict) and 
                      transaction.get("action") == "token_creation" and 
                      "tokens" in transaction):
                    for token_data in transaction["tokens"]:
                        if token_data.get("identifier") == token_id:
                            creation_info = {
                                "action": "creation",
                                "token_id": token_id,
                                "timestamp": block.timestamp,
                                "block_hash": block.hash,
                                "block_index": block.index
                            }
                            token_transactions.append(creation_info)
        return token_transactions

    def get_token_by_index(self, index):
        """Récupère un token par son index dans la liste des tokens."""
        all_tokens = self.token_manager.get_all_tokens()
        if 0 <= index < len(all_tokens):
            return all_tokens[index]
        return None

    def get_staking_stats(self):
        all_tokens = self.token_manager.get_all_tokens()
        total_tokens = len(all_tokens)
        total_staked = sum(len(wallet.staked_tokens) for wallet in self.wallet_manager.wallets.values())
        staking_percentage = (total_staked / total_tokens * 100) if total_tokens > 0 else 0
        total_value = self.token_manager.get_tokens_value()
        single_value = total_value / total_tokens if total_tokens > 0 else 0
        return {
            "total_tokens": total_tokens,
            "staking_tokens": total_staked,
            "staking_percentage": staking_percentage,
            "total_value": total_value,
            "staking_value": single_value * total_staked
        }

    def create_wallet_for_user(self, user_address, initial_credit=5):
        """
        Crée un nouveau wallet pour un utilisateur et le crédite automatiquement avec un nombre fixe de tokens
        provenant du wallet d'origine.
        """
        new_wallet = self.wallet_manager.create_wallet(user_address)
        origin = self.origin_wallet
        origin_wallet = self.wallet_manager.get_wallet(origin)
        available_tokens = list(origin_wallet.available_tokens)
        if len(available_tokens) < initial_credit:
            raise ValueError("Tokens insuffisants dans le wallet d'origine pour créditer le nouveau wallet")
        for token_id in available_tokens[:initial_credit]:
            self.transfer_token(token_id, origin, user_address)
        return new_wallet
