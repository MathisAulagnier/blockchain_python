# Importation des classes
from src.blockchain import Blockchain
from src.block import Block

# Création de la blockchain
my_blockchain = Blockchain()
print("Blockchain initialisée avec le bloc génésis :")

# Ajout de blocs
my_blockchain.add_block(["Lina envoie 10 BTC à Mathis"])
my_blockchain.add_block(["Mathis envoie 5 BTC à Lina"])


# Affichage des blocs
for block in my_blockchain.chain:
    print(block)

# Vérification de la validité de la blockchain
print("Blockchain valide ?", my_blockchain.is_chain_valid())