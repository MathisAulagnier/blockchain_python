import time
from src.block import Block
from src.blockchain import Blockchain
from src.pbft import PBFTConsensus

def main():
    # Initialisation de la blockchain PoS avec consensus PBFT
    blockchain = Blockchain()

    # Enregistrement de 4 validateurs avec des stakes différents
    blockchain.register_validator("Alice", 50)    # Stake élevé
    blockchain.register_validator("Bob", 30)      # Stake moyen
    blockchain.register_validator("Charlie", 10)  # Stake faible
    blockchain.register_validator("David", 10)    # Stake faible

    # Affichage des validateurs enregistrés et de leurs stakes
    print("Validateurs enregistrés avec leurs stakes :")
    for validator in blockchain.validators:
        print(f"{validator} : {blockchain.stakes[validator]}")

    # Initialisation du consensus PBFT avec la liste des validateurs enregistrés
    pbft = PBFTConsensus(blockchain.validators)

    # Ajout d'une transaction : Alice envoie 1 token à Bob
    transaction = "Alice envoie 1 token à Bob"
    blockchain.add_transaction(transaction)
    print("\nTransaction ajoutée :", transaction)

    # Simulation de la création du bloc candidat contenant les transactions en attente
    last_block = blockchain.get_last_block()
    candidate_block = Block(
        index=last_block.index + 1,
        previous_hash=last_block.hash,
        transactions=blockchain.pending_transactions,
        timestamp=time.time()
    )

    # Choix du validateur selon le mécanisme Proof of Stake (pondéré par le stake)
    chosen_validator = blockchain.choose_validator()
    print("\nValidateur choisi (Proof of Stake) :", chosen_validator)

    # Phase Pre-prepare : le leader (ici, le validateur choisi) propose le bloc candidat
    pre_prepare_msg = pbft.pre_prepare(candidate_block, leader=chosen_validator)
    print("\nPhase Pre-prepare :", pre_prepare_msg)

    # Phase Prepare : chaque validateur vote sur le bloc candidat
    # Pour simplifier, tous votent positivement (vote True)
    for validator in blockchain.validators:
        vote_msg = pbft.prepare(candidate_block, validator, vote=True)
        print("Phase Prepare -", vote_msg)

    # Phase Commit : vérifie que le bloc recueille au moins 2/3 des votes favorables
    commit_success, commit_msg = pbft.commit(candidate_block)
    print("\nPhase Commit :", commit_msg)

    if commit_success:
        # Génération de la signature PBFT pour le bloc validé
        consensus_signature = pbft.get_consensus_signature(candidate_block)
        print("Signature PBFT générée :", consensus_signature)
        # Ajoute le nouveau bloc à la blockchain en intégrant le validateur choisi et la signature PBFT
        blockchain.add_block(chosen_validator, consensus_signature)
    else:
        print("Consensus échoué : le bloc n'est pas ajouté.")

    # Vérification de l'intégrité globale de la blockchain
    is_valid = blockchain.is_chain_valid()
    print("\nValidité de la blockchain :", is_valid)

    # Affichage détaillé de la chaîne de blocs
    print("\nChaîne de blocs :")
    for block in blockchain.chain:
        block.print_block()

if __name__ == "__main__":
    main()
