###################
#### ATTENTION ####
# NE RENOMMEZ PAS #
## CE FICHIER !  ##
###################

# Le fichier indexation utilise la librairie yfinance 
# Qui utilise la librairie token! Danger -> from token import *


import uuid
import json
import hashlib
from datetime import datetime
from src.indexation import get_value



class Token:
    def __init__(self):
        self.identifier = str(uuid.uuid4())
        self.staking = False
        self.created_at = datetime.now().timestamp()
        self.hash = self.calculate_hash()
        
    def calculate_hash(self):
        """Calcule un hash unique pour ce token basé sur ses attributs"""
        token_string = json.dumps({
            "identifier": self.identifier,
            # "staking": self.staking, # Doit rester le même hash tout le temps
            "created_at": self.created_at
        }, sort_keys=True).encode()
        return hashlib.sha256(token_string).hexdigest()
    
        
    def toggle_staking(self):
        """Active ou désactive le staking pour ce token"""
        self.staking = not self.staking
        self.hash = self.calculate_hash()
        
    def to_dict(self):
        """Convertit le token en dictionnaire"""
        return {
            "identifier": self.identifier,
            "staking": self.staking,
            "created_at": self.created_at,
            "hash": self.hash
        }
    
    def __repr__(self):
        return f"Token(id={self.identifier[:8]}..., staking={self.staking})"
