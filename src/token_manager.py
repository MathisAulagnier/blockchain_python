import time
from src.token_ import Token

class TokenManager:
    def __init__(self, max_tokens=100):
        self.tokens = {}
        self.max_tokens = max_tokens
        
    def create_token(self):
        """Crée un nouveau token s'il reste des places disponibles"""
        if len(self.tokens) >= self.max_tokens:
            raise ValueError(f"Nombre maximum de tokens atteint ({self.max_tokens})")
        
        token = Token()
        self.tokens[token.identifier] = token
        return token
    
    def create_initial_tokens(self, count=100):
        """Crée le nombre défini de tokens initiaux"""
        created_tokens = []
        for _ in range(min(count, self.max_tokens - len(self.tokens))):
            token = self.create_token()
            created_tokens.append(token)
        return created_tokens
    
    def get_token(self, token_id):
        """Récupère un token par son identifiant"""
        return self.tokens.get(token_id)
    
    def get_all_tokens(self):
        return list(self.tokens.values())
    
    # N'existe pas car les la gestion des tokens en staking est gérée par le wallet
    # def get_staking_tokens(self): 
       # return [token for token in self.tokens.values() if token.staking]
    
    def get_tokens_value(self):
        """Calcule la valeur totale de tous les tokens"""
        if not self.tokens:
            return 0
            
        # Tous les tokens ont la même valeur dans votre implémentation
        # On prend donc la valeur d'un seul token et on multiplie par le nombre
        single_value = next(iter(self.tokens.values())).get_value()
        return single_value * len(self.tokens)
    
    # A supprimer car la gestion des tokens en staking est gérée par le wallet
    # def get_staking_tokens_value(self):
        # """Calcule la valeur totale des tokens en staking"""
        # staking_tokens = self.get_staking_tokens()
        # if not staking_tokens:
        #     return 0
            
        # single_value = staking_tokens[0].get_value()
        # return single_value * len(staking_tokens)
  