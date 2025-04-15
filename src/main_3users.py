# main_3users.py
from src.blockchain_manager import BlockchainManager
import time

if __name__ == "__main__":
    # --- Initialisation de la blockchain ---
    # Ici, nous démarrons la blockchain avec une offre initiale (par exemple, 100 tokens).
    bc_manager = BlockchainManager(initial_supply=100, origin_wallet="wallet_creator", transaction_threshold=2)
    
    # --- Création des wallets pour les 3 utilisateurs ---
    # On crée et crédite chaque wallet avec 5 tokens (par exemple).
    print("Création des wallets pour les 3 utilisateurs...")
    utilisateur_1 = bc_manager.create_wallet_for_user("utilisateur_1", initial_credit=5)
    utilisateur_2 = bc_manager.create_wallet_for_user("utilisateur_2", initial_credit=5)
    utilisateur_3 = bc_manager.create_wallet_for_user("utilisateur_3", initial_credit=5)
    
    # Petite pause pour observer la création
    time.sleep(1)
    
    # --- Scénario 1 : Utilisateur 1 effectue du staking de 2 tokens ---
    print("\nUtilisateur 1 effectue le staking de 2 tokens...")
    wallet_u1 = bc_manager.wallet_manager.get_wallet("utilisateur_1")
    available_tokens_u1 = list(wallet_u1.available_tokens)
    
    if len(available_tokens_u1) < 2:
        print("Utilisateur 1 n'a pas assez de tokens disponibles pour staker.")
    else:
        # On stake les 2 premiers tokens disponibles
        for i in range(2):
            token_id = available_tokens_u1[i]
            try:
                bc_manager.stake_token(token_id, "utilisateur_1")
                print(f"Token {token_id} staké par utilisateur 1")
            except Exception as e:
                print(f"[ERREUR] {e}")
    
    # --- Scénario 2 : Utilisateur 2 transfère un token à Utilisateur 3 ---
    print("\nUtilisateur 2 transfère un token à Utilisateur 3...")
    wallet_u2 = bc_manager.wallet_manager.get_wallet("utilisateur_2")
    available_tokens_u2 = list(wallet_u2.available_tokens)
    
    if not available_tokens_u2:
        print("Utilisateur 2 n'a aucun token disponible pour le transfert.")
    else:
        token_to_transfer = available_tokens_u2[0]
        try:
            bc_manager.transfer_token(token_to_transfer, "utilisateur_2", "utilisateur_3")
            print(f"Token {token_to_transfer} transféré de utilisateur 2 à utilisateur 3")
        except Exception as e:
            print(f"[ERREUR] {e}")
    
    # --- Commit manuel (si nécessaire) ---
    # Selon le seuil de transactions défini, il se peut que le commit se déclenche automatiquement.
    # Si vous souhaitez forcer le commit, vous pouvez appeler :
    print("\nCommit des transactions en attente...")
    bc_manager.commit_pending_transactions()
    
    # --- Affichage final des wallets et des blocs ---
    print("\n--- Etat final des wallets ---")
    for address, wallet in bc_manager.wallet_manager.wallets.items():
        print(f"{address} -> {wallet}")
    
    print("\n--- Affichage des blocs dans la blockchain ---")
    for block in bc_manager.chain:
        block.print_block()