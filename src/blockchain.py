from src.block import Block
import time

class Blockchain:
    def __init__(self):

        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []  # Transactions en attente d'inclusion dans un bloc
        self.validators = []            # Liste des identifiants des validateurs
        self.stakes = {}                # Dictionnaire associant chaque validateur à son montant de stake

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

    def get_last_block(self):
        """
        Retourne le dernier bloc de la chaîne.
        """
        return self.chain[-1]

    def add_action(self, transaction, pbft_instance=None):
        """
        Ajoute une action (transaction) à la liste des actions en attente.
        Si une instance PBFT est passée et que le nombre d'actions en attente >= 2,
        le processus de consensus PBFT est lancé automatiquement.
        :param transaction: Données de la transaction à ajouter.
        :param pbft_instance: Instance de PBFTConsensus (optionnel) pour lancer le consensus.
        """
        self.pending_transactions.append(transaction)
        # Déclenche le processus PBFT dès que 2 actions sont en attente et que pbft_instance est fourni.
        if pbft_instance and len(self.pending_transactions) >= 1:
            self.try_process_pending_actions(pbft_instance)

    def try_process_pending_actions(self, pbft_instance):
        """
        Lance le processus de consensus PBFT si le nombre d'actions en attente atteint
        ou dépasse 2. Cette méthode crée un bloc candidat à partir des actions en attente,
        choisit un validateur et déclenche successivement les phases Pre-prepare,
        Prepare et Commit du consensus PBFT.
        Si le consensus aboutit, le bloc est ajouté à la chaîne.
        :param pbft_instance: Instance de PBFTConsensus utilisée pour le processus de consensus.
        """
        if len(self.pending_transactions) >= 2:
            # Sélection d'un validateur (qui jouera le rôle de leader)
            validator = self.choose_validator()
            last_block = self.get_last_block()
            # Création d'un bloc candidat avec l'ensemble des actions en attente
            candidate_block = Block(
                index=last_block.index + 1,
                previous_hash=last_block.hash,
                transactions=self.pending_transactions,
                timestamp=time.time()
            )
            # Phase Pre-prepare : le leader (ici, le validateur choisi) propose le bloc
            pre_prepare_msg = pbft_instance.pre_prepare(candidate_block, leader=validator)
            print(pre_prepare_msg)
            # Phase Prepare : chaque validateur vote sur le bloc proposé
            for v in self.validators:
                vote_msg = pbft_instance.prepare(candidate_block, v, True)
                print(vote_msg)
            # Phase Commit : vérification que le bloc recueille suffisamment de votes favorables
            success, commit_msg = pbft_instance.commit(candidate_block)
            print(commit_msg)
            if success:
                consensus_signature = pbft_instance.get_consensus_signature(candidate_block)
                # Ajoute le bloc à la chaîne en enregistrant le validateur et la signature PBFT
                self.add_block(validator, consensus_signature)
            else:
                print("Consensus PBFT échoué, le bloc n'est pas ajouté.")

    def register_validator(self, validator, stake):
        """
        Enregistre un validateur en ajoutant le montant de stake indiqué.
        Si le validateur est déjà enregistré, son stake est incrémenté.
        :param validator: Identifiant du validateur (exemple, adresse ou nom)
        :param stake: Montant de stake à ajouter pour ce validateur
        """
        if validator not in self.validators:
            self.validators.append(validator)
        self.stakes[validator] = self.stakes.get(validator, 0) + stake

    def choose_validator(self):
        """
        Sélectionne un validateur de manière pondérée en fonction du stake.
        Un nombre aléatoire est tiré pour choisir parmi les validateurs en proportion de leur stake.
        :return: L'identifiant du validateur sélectionné
        """
        total_stake = sum(self.stakes.values())
        import random
        pick = random.uniform(0, total_stake)
        current = 0
        for validator, stake in self.stakes.items():
            current += stake
            if current > pick:
                return validator
        return None

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
            timestamp=time.time()
        )
        # Ajout des attributs spécifiques à PoS et PBFT
        new_block.validator = validator
        new_block.pbft_signature = pbft_signature
        self.chain.append(new_block)
        self.pending_transactions = []

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
                return False
            if current.timestamp < previous.timestamp:
                return False
            if current.previous_hash != previous.hash:
                return False
        return True
