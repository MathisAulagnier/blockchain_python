from src.block import Block
import time
import random

class Blockchain:
    def __init__(self):

        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        """
        Crée le bloc génésis de la blockchain.
        """
        return Block(
            index=0,
            previous_hash="0",
            transactions=["Genesis Block"],
            timestamp=time.time()
        )
    
    def create_candidate_block(self, transactions):
        """
        Crée un bloc candidat à partir des transactions données.
        Ce bloc n'est pas encore ajouté à la chaîne, il sert à la validation via le consensus.
        """
        last_block = self.get_last_block()
        candidate = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            transactions=transactions,
            timestamp=time.time()
        )
        return candidate


    def get_last_block(self):
        """
        Retourne le dernier bloc de la chaîne.
        """
        return self.chain[-1]

    def add_transaction(self, transaction):
        """
        Ajoute une transaction à la liste des transactions en attente.
        :param transaction: Données de la transaction à ajouter
        """
        self.pending_transactions.append(transaction)



    def add_block(self, validator, pbft_signature):
        """
        Ajoute un nouveau bloc à la chaîne à partir des transactions en attente.
        Le bloc est validé par le validateur sélectionné et reçoit une signature issue du consensus PBFT.
        Après ajout, la liste des transactions en attente est vidée.
        :param validator: Identifiant du validateur ayant validé le bloc
        :param pbft_signature: Signature générée via le consensus PBFT
        """
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            transactions=self.pending_transactions,
            timestamp=time.time(),
            validator = validator,
            pbft_signature = pbft_signature
        )
        # Ajout des attributs spécifiques à PoS et PBFT
        
        self.chain.append(new_block)
        self.pending_transactions = []
        print(f"Block {new_block.index} ajouté avec succès !")

    def is_chain_valid(self):
        """
        Vérifie l'intégrité de la blockchain en s'assurant que :
          - Le hash de chaque bloc correspond bien au recalcul de ses données.
          - Les timestamps sont cohérents (le bloc courant est créé après le précédent).
          - Chaque bloc référence correctement le hash du bloc précédent.
        :return: True si la blockchain est valide, False sinon.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                print(f"Hash mismatch at block {current.index}")
                return False
                
            if current.timestamp < previous.timestamp:
                print(f"Timestamp mismatch at block {current.index}")
                return False
            if current.previous_hash != previous.hash:
                print(f"Previous hash mismatch at block {current.index}")
                return False
        return True
