class PBFT:

    def __init__(self, validators, stakes):
        self.validators = validators
        self.stakes = stakes
        # Dictionnaires pour stocker les messages et votes par index de bloc
        self.pre_prepare_messages = {}  # Exemple : {block_index: {"block": block, "leader": leader}}
        self.prepare_votes = {}         # Exemple : {block_index: {validator: vote}}
        self.commit_votes = {}          # Exemple : {block_index: {validator: vote}}

    def pre_prepare(self, block, leader):
        """
        Phase Pre-prepare : le leader propose un bloc.
        Enregistre le message de pré-proposition.
        :param block: Bloc proposé
        :param leader: Identifiant du leader
        :return: Message de pré-proposition
        """
        self.pre_prepare_messages[block.index] = {"block": block, "leader": leader}
        return f"Pre-prepare: Bloc {block.index} proposé par le leader {leader}"

    def prepare(self, block, validator, vote):
        """
        Phase Prepare : chaque nœud valide localement le bloc et vote.
        :param block: Bloc sur lequel voter
        :param validator: Identifiant du validateur qui vote
        :param vote: Vote exprimé (True pour approuver, False pour rejeter)
        :return: Message de vote en phase prepare
        """
        if block.index not in self.prepare_votes:
            self.prepare_votes[block.index] = {}
        self.prepare_votes[block.index][validator] = vote
        return f"Prepare: Validator {validator} a voté {vote} pour le Bloc {block.index}"

    def commit(self, block):
        """
        Phase Commit : Vérifie si le bloc recueille au moins 2/3 des votes favorables pondérés par le stake.
        Pour chaque validateur ayant voté, son vote compte avec un poids correspondant à son stake.
        """
        votes = self.prepare_votes.get(block.index, {})
        weighted_total = sum(self.stakes.get(v, 0) for v in self.validators if v in votes)
        weighted_positive = sum(self.stakes.get(v, 0) for v, vote in votes.items() if vote)
        
        if weighted_total > 0 and weighted_positive >= (2 * weighted_total) / 3:
            self.commit_votes[block.index] = votes
            return True, f"Commit: Bloc {block.index} validé avec un poids positif de {weighted_positive}/{weighted_total}."
        else:
            return False, f"Commit: Bloc {block.index} rejeté avec un poids positif de {weighted_positive}/{weighted_total}."

    def get_consensus_signature(self, block):
        """
        Simule la génération d'une signature de consensus PBFT pour le bloc.
        :param block: Bloc validé
        :return: Chaîne représentant la signature (pour simplification)
        """
        return f"PBFT_Signature_Block_{block.index}"
