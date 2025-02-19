import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Génère le hash du bloc à partir de son contenu.
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    
    
    def __repr__(self):
        return f"Block({self.index}, {self.previous_hash}, {self.timestamp}, {self.transactions}, {self.nonce}, {self.hash})"