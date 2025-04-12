from src.blockchain_manager import BlockchainManager
import time

if __name__ == "__main__":
    # --- Initialisation de la blockchain ---
    # Lors de l'instanciation, create_initial_supply est appelée et crée :
    #   - wallet_creator (wallet d'origine)
    #   - wallet_Lina (10 tokens, 1 token staké)
    #   - wallet_Mathis (15 tokens, 1 token staké)
    #   - wallet_JJ (20 tokens, 1 token staké)
    token_chain = BlockchainManager(initial_supply=100, origin_wallet="wallet_creator")
    print("Blockchain initialisée avec l'offre initiale, wallets de base créés et validateurs inscrits.\n")
    
    # Affichage du seuil de transaction
    print(f"Transaction threshold: {token_chain.transaction_threshold}\n")
    
    # Affichage des blocs post-initialisation (excluant bloc 0 et bloc 1)
    print("Affichage des blocs post-initialisation :")
    for block in token_chain.chain:
        block.print_block()
    print("-------------------------------------------------------\n")
    
    # Affichage des wallets actuels
    print("Liste des wallets actuels :")
    for address, wallet in token_chain.wallet_manager.wallets.items():
        print(f"Adresse : {address} -> {wallet}")
    print("-------------------------------------------------------\n")
    
    # Affichage des validateurs initiaux
    print("Liste des validateurs initiaux (wallets ayant staké) :")
    if token_chain.validators:
        for validator in token_chain.validators:
            print(f"{validator} -> stake: {token_chain.stakes.get(validator, 0)}")
    else:
        print("Aucun validateur enregistré.")
    print("-------------------------------------------------------\n")
    
    input("Appuyez sur Entrée pour lancer la première simulation de votes & staking...\n")
    
    # --- Première simulation ---
    # On définit manuellement les votes pour la prochaine opération de commit
    # wallet_JJ vote True, wallet_Lina vote False, wallet_Mathis vote True.
    token_chain.manual_votes = {
        "wallet_JJ": True,
        "wallet_Lina": True,
        "wallet_Mathis": False
    }
    print("Votes manuels définis pour la première simulation :")
    print("  wallet_JJ -> True")
    print("  wallet_Lina -> True")
    print("  wallet_Mathis -> False")
    print("-------------------------------------------------------\n")

    # wallet creator transfert 12 crédéit à wallet JJ
    wallet_creator = token_chain.wallet_manager.get_wallet("wallet_creator")
    for i in range(12):
        if wallet_creator.available_tokens:
            token_id = list(wallet_creator.available_tokens)[0]
            print(f"Transaction {i+1}: wallet_creator transfère un token à wallet_JJ")
            token_chain.transfer_token(token_id, "wallet_creator", "wallet_JJ")
        else:
            print("wallet_creator n'a pas de token disponible pour la transaction.")
            break
    print("-------------------------------------------------------\n")
    
    # wallet creator transfert 2 crédit à wallet lina 
    for i in range(2):
        if wallet_creator.available_tokens:
            token_id = list(wallet_creator.available_tokens)[0]
            print(f"Transaction {i+1}: wallet_creator transfère un token à wallet_Lina")
            token_chain.transfer_token(token_id, "wallet_creator", "wallet_Lina")
        else:
            print("wallet_creator n'a pas de token disponible pour la transaction.")
            break

    # wallet creator transfert 2 crédit à wallet mathis
    for i in range(2):
        if wallet_creator.available_tokens:
            token_id = list(wallet_creator.available_tokens)[0]
            print(f"Transaction {i+1}: wallet_creator transfère un token à wallet_Mathis")
            token_chain.transfer_token(token_id, "wallet_creator", "wallet_Mathis")
        else:
            print("wallet_creator n'a pas de token disponible pour la transaction.")
            break
    print("-------------------------------------------------------\n")
    # Simulation : wallet_JJ va stacker 8 tokens supplémentaires
    print("wallet_JJ effectue 8 additional staking...")
    wallet_jj = token_chain.wallet_manager.get_wallet("wallet_JJ")
    for i in range(8):
        if wallet_jj.available_tokens:
            token_id = list(wallet_jj.available_tokens)[0]
            token_chain.stake_token(token_id, "wallet_JJ")
        else:
            print("  wallet_JJ n'a plus de tokens disponibles pour staker.")
            break
    print("-------------------------------------------------------\n")
    
    # Lancement du commit : ce commit va intégrer toutes les transactions de staking supplémentaires.
    print("Commit des transactions (première simulation)...")
    token_chain.commit_pending_transactions()
    print("-------------------------------------------------------\n")
    
    # Affichage des blocs post-initialisation (sauf bloc 0 et 1)
    print("Blocs post-initialisation après première simulation:")
    for block in token_chain.chain[2:]:
        block.print_block()
    print("-------------------------------------------------------\n")
    
    # Affichage de la liste des validateurs après la première simulation
    print("Liste des validateurs après la première simulation :")
    if token_chain.validators:
        for validator in token_chain.validators:
            print(f"{validator} -> stake: {token_chain.stakes.get(validator, 0)}")
    else:
        print("Aucun validateur enregistré.")
    print("-------------------------------------------------------\n")
    
    input("Appuyez sur Entrée pour lancer la seconde simulation de transaction et votes...\n")
    
    # --- Seconde simulation ---
    # On simule une transaction simple de 2 tokens : wallet_Lina transfère 2 tokens à wallet_Mathis.
    token_chain.manual_votes = {
        "wallet_JJ": False,
        "wallet_Lina": True,
        "wallet_Mathis": True
    }
    
    print("Votes manuels définis pour la seconde simulation :")
    print("  wallet_JJ -> False")
    print("  wallet_Lina -> True")
    print("  wallet_Mathis -> True")
    print("-------------------------------------------------------\n")
    wallet_lina = token_chain.wallet_manager.get_wallet("wallet_Lina")
    for j in range(2):
        if wallet_lina.available_tokens:
            token_id = list(wallet_lina.available_tokens)[0]
            print(f"Transaction {j+1} (seconde simulation): wallet_Lina transfère un token à wallet_Mathis")
            token_chain.transfer_token(token_id, "wallet_Lina", "wallet_Mathis")
        else:
            print("wallet_Lina n'a pas de token disponible pour la transaction.")
            break
    print("-------------------------------------------------------\n")
    
    # Pour cette seconde simulation, on définit manuellement les votes suivants :
    # wallet_JJ vote False, wallet_Lina vote True, wallet_Mathis vote True

    
    # Lancement du commit pour la seconde simulation.
    print("Commit des transactions (seconde simulation)...")
    token_chain.commit_pending_transactions()
    print("-------------------------------------------------------\n")
    
    # --- Affichage final ---
    print("Liste mise à jour des validateurs :")
    if token_chain.validators:
        for validator in token_chain.validators:
            print(f"{validator} -> stake: {token_chain.stakes.get(validator, 0)}")
    else:
        print("Aucun validateur enregistré.")
    print("-------------------------------------------------------\n")
    
    print("Affichage complet des blocs post-initialisation (genèse et initialisation exclus) :")
    for block in token_chain.chain[2:]:
        block.print_block()
