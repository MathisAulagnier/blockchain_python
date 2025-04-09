###################
#### ATTENTION ####
##### NE  PAS #####
#### SUPPRIMER ####
## CE FICHIER !  ##
###################

# Vous pouvez le renommer blockchain_pow.py
# Pour ensuite ecrire votre propre blockchain en PoA


from src.block_pow import BlockPow

import time
import hashlib

class BlockchainPow:
    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        """
        Crée le premier bloc de la blockchain (bloc génésis).
        """
        return BlockPow(
            index=0,
            previous_hash="0",
            transactions=["Genesis Block"],
            difficulty=self.difficulty
        )
    
    def get_last_block(self):
        """
        Retourne le dernier bloc de la chaîne.
        """
        return self.chain[-1]

    def add_block(self, transactions):
        """
        Ajoute un nouveau bloc avec une liste de transactions.
        """
        last_block = self.get_last_block()
        new_block = BlockPow(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            transactions=transactions,
            difficulty=self.difficulty
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Vérifie que la blockchain est valide (chaînage correct des hashes).
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Vérifie si le hash du bloc est bien calculé
            if current.hash != current.calculate_hash():
                return False
            
            # Vérifie si le block de pointe est crée après le précédent
            if current.timestamp < previous.timestamp:
                return False
            
            # Vérifie si le bloc pointe correctement vers le précédent
            if current.previous_hash != previous.hash:
                return False

        return True
    


