import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp=None, validator=None, pbft_signature=None):
        """
        Initialise un bloc de la blockchain en configurant ses données et en calculant son hash.
        Les attributs validator et pbft_signature sont initialisés à None.
        :param index: l'indice du bloc dans la chaîne
        :param previous_hash: le hash du bloc précédent
        :param transactions: la liste des transactions à inclure dans le bloc
        :param timestamp: l'horodatage du bloc, ou le temps actuel si None
        """
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        # Initialisation des attributs pour Proof of Stake (PoS) et consensus PBFT
        self.validator = validator
        self.pbft_signature = pbft_signature
        # Calcule immédiatement le hash sans processus de minage
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calcule le hash du bloc en utilisant SHA-256 sur un dictionnaire des données du bloc.
        Les attributs validator et pbft_signature sont inclus pour garantir l'intégrité dans le contexte PoS/PBFT.
        :return: Le hash du bloc sous forme de chaîne hexadécimale.
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "pbft_signature": self.pbft_signature
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

    def print_block(self):
        """
        Affiche les informations essentielles du bloc pour le débogage ou la visualisation.
        """
        print(f'__Block n° {self.index} __')
        print(f'Hash précédent : {self.previous_hash[:10]}')
        print(f'Date : {self.timestamp}')
        print(f'Nombre de transactions : {len(self.transactions)}')
        print(f'Transactions : {self.transactions}')
        print(f'Hash du bloc: {self.hash[:10]}')
        print(f'Validateur : {self.validator}')
        print(f'Signature PBFT : {self.pbft_signature}')
        print('_______________\n')

    def __repr__(self):
        return f"Block({self.index}, {self.previous_hash}, {self.timestamp}, {self.transactions}, {self.hash})"
