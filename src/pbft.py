class PBFTConsensus:

    def __init__(self, validators):
        self.validators = validators
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
        Phase Commit : Vérifie si le bloc recueille au moins 2/3 des votes favorables.
        Si oui, le bloc est considéré comme commité.
        :param block: Bloc en cours de validation
        :return: Tuple (booléen indiquant le succès, message descriptif)
        """
        votes = self.prepare_votes.get(block.index, {})
        total_votes = len(votes)
        positive_votes = sum(1 for v in votes.values() if v is True)
        if total_votes >= len(self.validators) and positive_votes >= (2 * len(self.validators)) / 3:
            self.commit_votes[block.index] = votes
            return True, f"Commit: Bloc {block.index} validé avec {positive_votes}/{len(self.validators)} votes favorables."
        else:
            return False, f"Commit: Bloc {block.index} rejeté avec {positive_votes}/{len(self.validators)} votes favorables."

    def get_consensus_signature(self, block):
        """
        Simule la génération d'une signature de consensus PBFT pour le bloc.
        :param block: Bloc validé
        :return: Chaîne représentant la signature (pour simplification)
        """
        return f"PBFT_Signature_Block_{block.index}"
