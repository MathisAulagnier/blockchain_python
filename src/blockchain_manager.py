import time
from src.blockchain import Blockchain
from src.token_manager import TokenManager
from src.wallet_manager import WalletManager


# Address : représente une adresse de portefeuille


class BlockchainManager(Blockchain):
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager(max_tokens=100)
        self.wallet_manager = WalletManager()
        
    def create_initial_supply(self, count=100, owner_address="wallet_creator"):
        """Crée l'offre initiale de tokens et l'attribue au wallet 'owner_address'"""
        tokens = self.token_manager.create_initial_tokens(count)
        # Pour chaque token, on l'attribue au wallet créateur.
        for token in tokens:
            self.wallet_manager.deposit(owner_address, token.identifier, stake=False)
        token_data = [token.to_dict() for token in tokens]
        # IMPORTANT : On passe une liste contenant la transaction de création
        self.add_action([{"action": "token_creation", "owner": owner_address, "tokens": token_data}])
        return tokens

    
    def transfer_token(self, token_id, from_address, to_address):
        """Enregistre un transfert de token dans la blockchain d'un wallet à un autre"""
        # Récupération des wallets source et destination
        from_wallet = self.wallet_manager.get_wallet(from_address)
        to_wallet = self.wallet_manager.get_wallet(to_address)
        
        # Vérifier que le token appartient bien au wallet source et qu'il n'est pas staké
        if token_id not in from_wallet.available_tokens:
            raise ValueError(f"Token {token_id} n'est pas disponible dans le wallet {from_address} (peut être en staking)")
        
        # Effectuer le transfert
        from_wallet.withdraw_token(token_id)
        to_wallet.deposit_token(token_id, stake=False)

        transaction = {
            "action": "transfer",
            "token_id": token_id,
            "from": from_address,
            "to": to_address,
            "timestamp": time.time()
        }
        self.add_action([transaction])
        return transaction
    
    def stake_token(self, token_id, address):
        """Met un token en staking : déplace le token du solde disponible vers le solde staké du wallet."""
        wallet = self.wallet_manager.get_wallet(address)
        # Vérifier que le token est disponible pour staking
        if token_id not in wallet.available_tokens:
            raise ValueError(f"Token {token_id} n'est pas disponible dans le wallet {address} pour être staké")
        
        # Déplacer le token dans le solde staké (géré uniquement par le wallet)
        wallet.stake_token(token_id)
        
        transaction = {
            "action": "stake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_action([transaction])
        return transaction
    
    def unstake_token(self, token_id, address):
        """Retire un token du staking : déplace le token du solde staké vers le solde disponible du wallet."""
        wallet = self.wallet_manager.get_wallet(address)
        # Vérifier que le token est actuellement staké
        if token_id not in wallet.staked_tokens:
            raise ValueError(f"Token {token_id} n'est pas en staking dans le wallet {address}")
        
        # Déplacer le token du staking vers le solde disponible
        wallet.unstake_token(token_id)
        
        transaction = {
            "action": "unstake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_action([transaction])
        return transaction

    def get_token_history(self, token_id):
        """Retourne l'historique des transactions pour un token spécifique"""
        token_transactions = []
        
        for block in self.chain:
            for transaction in block.transactions:
                # Vérifie si c'est un dictionnaire et s'il contient token_id
                if isinstance(transaction, dict) and transaction.get("token_id") == token_id:
                    # Ajoute le hash du bloc et l'index pour référence
                    transaction_with_block = transaction.copy()
                    transaction_with_block["block_hash"] = block.hash
                    transaction_with_block["block_index"] = block.index
                    token_transactions.append(transaction_with_block)
                
                # Vérifie aussi dans les transactions de création groupées
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
        """Récupère un token par son index dans la liste (0-99)"""
        # Inutile pour le moment
        all_tokens = self.token_manager.get_all_tokens()
        if 0 <= index < len(all_tokens):
            return all_tokens[index]
        return None
    
    #A refaire
    def get_staking_stats(self):
        """Retourne des statistiques sur les tokens en staking"""
        all_tokens = self.token_manager.get_all_tokens()
        staking_tokens = self.token_manager.get_staking_tokens()
        
        return {
            "total_tokens": len(all_tokens),
            "staking_tokens": len(staking_tokens),
            "staking_percentage": (len(staking_tokens) / len(all_tokens) * 100) if all_tokens else 0,
            "total_value": self.token_manager.get_tokens_value(),
            "staking_value": self.token_manager.get_staking_tokens_value()
        }
        
    def get_staking_stats(self):
        all_tokens = self.token_manager.get_all_tokens()
        total_tokens = len(all_tokens)
        
        # Agrégation des tokens stakés à partir de tous les wallets
        total_staked = sum(len(wallet.staked_tokens) for wallet in self.wallet_manager.wallets.values())
        
        staking_percentage = (total_staked / total_tokens * 100) if total_tokens > 0 else 0
        
        total_value = self.token_manager.get_tokens_value()
        # Dans cet exemple, tous les tokens ont la même valeur (récupérée par get_value())
        single_value = total_value / total_tokens if total_tokens > 0 else 0
        
        return {
            "total_tokens": total_tokens,
            "staking_tokens": total_staked,
            "staking_percentage": staking_percentage,
            "total_value": total_value,
            "staking_value": single_value * total_staked
        }