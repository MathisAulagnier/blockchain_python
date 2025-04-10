from src.blockchain_manager import BlockchainManager
from src.token_ import Token

if __name__ == "__main__":
    # Créer la blockchain en précisant la difficulté, le nombre initial de tokens et le wallet d'origine
    token_chain = BlockchainManager(difficulty=2, initial_supply=100, origin_wallet="wallet_creator")
    
    # Créer des wallets pour d'autres utilisateurs, crédités automatiquement
    wallet_mathis = token_chain.create_wallet_for_user("wallet_Mathis", initial_credit=10)
    wallet_lina = token_chain.create_wallet_for_user("wallet_Lina", initial_credit=5)

    print("Offre initiale créée et wallets crédités.")

    # Afficher quelques tokens de l'origine
    initial_tokens = token_chain.token_manager.get_all_tokens()
    print("\nInformation sur les 5 premiers tokens de l'origine:")
    for i in range(5):
        print(initial_tokens[i])
        print(f"Valeur actuelle: {initial_tokens[i].get_value()}")

    # Parfois, on souhaite forcer l'enregistrement des transactions en attente
    # Par exemple, après plusieurs transferts ou opérations
    print("\nCommit des transactions en attente...")
    token_chain.commit_pending_transactions()

    # Afficher l'historique du premier token
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
