from src.token_blockchain import TokenBlockchain
from src.token_ import Token


if __name__ == "__main__":
    token_chain = TokenBlockchain(difficulty=2)

    print("Création de l'offre initiale de tokens...")
    initial_tokens = token_chain.create_initial_supply(count=100)
    print(f"Nombre de tokens créés: {len(initial_tokens)}")
    
    print("\nInformation sur les 5 premires Tokens:")
    for i in range(5):
        print(initial_tokens[i])
        print(f"Valeur actuelle: {initial_tokens[i].get_value()}")
    
    # Simuler des transferts de tokens
    print("\nSimulation de transferts...")
    Mathis = "wallet_Mathis"
    Lina = "wallet_Lina"
    
    token_id = initial_tokens[0].identifier
    # ICI 
    # Voir comment on répartit les tokens entre les utilisateurs
    # (non implémenté)
    # ICI
    token_chain.transfer_token(token_id, Mathis, Lina)
    
    # Mettre des tokens en staking
    print("\nMise en staking de tokens...")
    for i in range(10):  # Mettre 10 premiers tokens en staking
        token_id = initial_tokens[i].identifier
        token_chain.stake_token(token_id, Mathis)
    
    # Vérifier les tokens en staking
    staking_tokens = token_chain.token_manager.get_staking_tokens()
    print(f"Nombre de tokens en staking: {len(staking_tokens)}")
    
    # Afficher les statistiques de staking
    stats = token_chain.get_staking_stats()
    print("\nStatistiques de staking:")
    print(f"Total des tokens: {stats['total_tokens']}")
    print(f"Tokens en staking: {stats['staking_tokens']} ({stats['staking_percentage']:.2f}%)")
    print(f"Valeur totale: {stats['total_value']}")
    print(f"Valeur en staking: {stats['staking_value']}")
    
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
    
    # Afficher un graphique de la valeur (nécessite la fonction plot_value_index)
    print("\nAffichage du graphique de valeur:")
    Token.plot_value(nb_days=30)
