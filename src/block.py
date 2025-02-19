import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Calculer le hash du bloc en concaténant les différentes informations
        block_string = str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data) + str(self.nonce)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def __repr__(self):
        return f"Block({self.index}, {self.previous_hash}, {self.timestamp}, {self.data}, {self.nonce}, {self.hash})"