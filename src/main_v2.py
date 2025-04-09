from src.blockchain_manager import BlockchainManager
from src.token_ import Token

if __name__ == "__main__":
    token_chain = BlockchainManager(difficulty=2)
    # Création explicite des wallets utilisés pour la simulation
    # On crée par exemple le wallet de Mathis et celui de Lina
    wallet_mathis = token_chain.wallet_manager.create_wallet("wallet_Mathis")
    wallet_lina = token_chain.wallet_manager.create_wallet("wallet_Lina")

    print("Création de l'offre initiale de tokens...")
    # Ici, on attribue tous les tokens initiaux au wallet de Mathis
    initial_tokens = token_chain.create_initial_supply(count=100, owner_address="wallet_Mathis")
    print(f"Nombre de tokens créés: {len(initial_tokens)}")

    print("\nInformation sur les 5 premiers Tokens:")
    for i in range(5):
        print(initial_tokens[i])
        print(f"Valeur actuelle: {initial_tokens[i].get_value()}")

    # Simulation de transfert : transfère un token du wallet de Mathis vers celui de Lina
    print("\nSimulation de transfert...")
    # Ici, on transfère par exemple le premier token de la liste
    token_id = initial_tokens[0].identifier
    token_chain.transfer_token(token_id, "wallet_Mathis", "wallet_Lina")

    # Mise en staking de tokens :
    # Plutôt que de prendre les 10 premiers de initial_tokens, qui ne reflètent plus l'état du wallet de Mathis,
    # on récupère les tokens disponibles dans le wallet de Mathis.
    print("\nMise en staking de tokens...")
    
    #Refaire des fonctions qui permettent de transferer plus simplement plusieurs token, selection les X premiers disponible, etc.
    mathis_wallet = token_chain.wallet_manager.get_wallet("wallet_Mathis")
    # Convertir le set available_tokens en liste pour pouvoir en prendre une tranche
    available_tokens = list(mathis_wallet.available_tokens)
    # On prend les 10 premiers tokens disponibles
    tokens_to_stake = available_tokens[:10]
    for token_id in tokens_to_stake:
        token_chain.stake_token(token_id, "wallet_Mathis")

    # Vérifier et afficher les statistiques de staking (calculées en agrégeant les soldes des wallets)
    stats = token_chain.get_staking_stats()
    print("\nStatistiques de staking:")
    print(f"Total des tokens: {stats['total_tokens']}")
    print(f"Tokens en staking: {stats['staking_tokens']} ({stats['staking_percentage']:.2f}%)")
    print(f"Valeur totale: {stats['total_value']}")
    print(f"Valeur en staking: {stats['staking_value']}")

    # Affichage de l'historique du premier token
    print("\nHistorique du premier token:")
    history = token_chain.get_token_history(initial_tokens[0].identifier)
    for event in history:
        print(f"Action: {event['action']} - Bloc: {event['block_index']}")

    # Afficher des informations sur la blockchain
    print("\nInformations sur la blockchain:")
    print(f"Nombre de blocs: {len(token_chain.chain)}")
    print(f"La chaîne est valide: {token_chain.is_chain_valid()}")

    # Afficher le dernier bloc
    print("\nDernier bloc:")
    token_chain.chain[-1].print_block()

    # Afficher un graphique de la valeur via plot_value_index
    print("\nAffichage du graphique de valeur:")
    Token.plot_value(nb_days=30)
