import time
from src.blockchain import Blockchain
from src.token_manager import TokenManager

# Address : représente une adresse de portefeuille


class TokenBlockchain(Blockchain):
    def __init__(self, difficulty=2):
        super().__init__(difficulty)
        self.token_manager = TokenManager(max_tokens=100)
        
    def create_initial_supply(self, count=100):
        """Crée l'offre initiale de tokens et l'enregistre dans un bloc"""
        tokens = self.token_manager.create_initial_tokens(count)
        token_data = [token.to_dict() for token in tokens]
        self.add_block({"action": "token_creation", "tokens": token_data})
        return tokens
    
    def transfer_token(self, token_id, from_address, to_address):
        """Enregistre un transfert de token dans la blockchain"""
        token = self.token_manager.get_token(token_id)
        if not token:
            raise ValueError(f"Token {token_id} n'existe pas")
        
        # ICI
        # Vérifier la solvabilité de l'adresse d'envoi
        # La possession du token
        # Vérifier que l'adresse d'envoi a le token
        # (non implémenté)
        # ICI

        transaction = {
            "action": "transfer",
            "token_id": token_id,
            "from": from_address,
            "to": to_address,
            "timestamp": time.time()
        }
        self.add_block([transaction])
        return transaction
    
    def stake_token(self, token_id, address):
        """Met un token en staking ou le retire du staking"""

        # Pour le parcours de l'arbre je propose de suivre l'evolution du stacking dans la blockchain
        # A discuter
        # ICI

        token = self.token_manager.get_token(token_id)
        if not token:
            raise ValueError(f"Token {token_id} n'existe pas")
        
        token.toggle_staking()
        # ICI
        # Possibilité de  stacker plusieurs tokens de l'utilisateur ou tout les tokens
        # Non implémenté
        # ICI
        
        transaction = {
            "action": "stake" if token.staking else "unstake",
            "token_id": token_id, 
            "address": address,
            "timestamp": time.time()
        }
        self.add_block([transaction])
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