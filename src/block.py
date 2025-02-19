import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=2, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.nonce = 0
        self.difficulty = difficulty 
        self.hash = self.mine_block()  # On mine le bloc dès sa création


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
    
    def mine_block(self):
        """
        Trouve un hash valide respectant la difficulté (Proof of Work).
        """
        while True:
            hash_attempt = self.calculate_hash()
            if hash_attempt[:self.difficulty] == "0" * self.difficulty:
                print(f"Bloc {self.index} miné : {hash_attempt}")
                return hash_attempt
            self.nonce += 1
    
    def print_block(self):
        print('__Block n°', self.index,"__")
        print('Hash precedent : ', self.previous_hash[:10])
        print('Date : ', self.timestamp)
        print("Nombre de transactions : ", len(self.transactions))
        print(self.transactions)
        print('Hash block:', self.hash[:10])
        print('Nonce : ', self.nonce)
        print('_______________\n')


    def __repr__(self):
        return f"Block({self.index}, {self.previous_hash}, {self.timestamp}, {self.transactions}, {self.nonce}, {self.hash})"