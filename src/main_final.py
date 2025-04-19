from src.blockchain_manager import BlockchainManager
import random
from src.token_ import Token

def display_menu():
    print("\n--- MENU PRINCIPAL ---")
    print("1. Menu Blockchain")
    print("2. Afficher l'état d'un wallet")
    print("3. Staker des tokens")
    print("4. Unstaker des tokens")
    print("5. Transférer des tokens")
    print("6. Créer un nouveau wallet")
    print("7. Charger un scénario de vote")
    print("8. Simuler du faux trafic")
    print("9. Quitter")
    print("----------------------")


def display_status(bc_manager):
    print("\n--- Statut de la blockchain ---")
    print(f"Hauteur de la blockchain : {len(bc_manager.chain)}")
    pending = bc_manager.pending_transactions
    threshold = bc_manager.transaction_threshold
    print(f"Transactions en attente : {len(pending)}/{threshold}")
    #afficher toutes les transactions en attente
    display_pending_transactions(bc_manager)
    
    tokens = bc_manager.token_manager.get_all_tokens()
    if tokens:
        total_value = bc_manager.token_manager.get_tokens_value()
        price = total_value / len(tokens)
    else:
        price = 0
    print(f"Cours moyen du token (USD) : {price}")
    print("------------------------\n")


def print_all_blocks(bc_manager):
    print("\n--- Tous les blocs ---")
    for block in bc_manager.chain:
        block.print_block()
    print("------------------------\n")


def print_block_by_index(bc_manager):
    try:
        idx = int(input("Index du bloc à afficher: ").strip())
        if 0 <= idx < len(bc_manager.chain):
            print(f"\n--- Bloc {idx} ---")
            bc_manager.chain[idx].print_block()
        else:
            print("Index hors limites.")
    except ValueError:
        print("Entrée invalide.")


def print_last_block(bc_manager):
    print("\n--- Dernier bloc ---")
    bc_manager.get_last_block().print_block()
    print("------------------------\n")

def display_pending_transactions(bc_manager):
    print("\n--- Transactions en attente ---")
    if bc_manager.pending_transactions:
        for i, tx in enumerate(bc_manager.pending_transactions, start=1):
            print(f"{i}. {tx}")
    else:
        print("Aucune transaction en attente.")
    print("-------------------------------\n")
    
    
def blockchain_menu(bc_manager):
    while True:
        print("\n--- Menu Blockchain ---")
        print("1. Statut global")
        print("2. Afficher tous les blocs")
        print("3. Afficher un bloc par index")
        print("4. Afficher le dernier bloc")
        print("5. Afficher les transactions en attente")
        print("6. Afficher le graphique de valeur")
        print("7. Retour au menu principal")
        
        choice = input("Choix: ").strip()
        if choice == '1':
            display_status(bc_manager)
        elif choice == '2':
            print_all_blocks(bc_manager)
        elif choice == '3':
            print_block_by_index(bc_manager)
        elif choice == '4':
            print_last_block(bc_manager)
        elif choice == '5':
            display_pending_transactions(bc_manager)
        elif choice == '6':
            print("\nAffichage du graphique de valeur:")
            Token.plot_value(nb_days=60)
        elif choice == '7':
            break
        else:
            print("Choix invalide, réessayez.")



def display_wallet_list(bc_manager):
    print("\nWallets disponibles :")
    for addr, w in bc_manager.wallet_manager.wallets.items():
        print(f"  - {addr} (available: {w.balance()}, staked: {w.staked_balance()})")


def display_wallet(bc_manager, address):
    if not address:
        return
    try:
        wallet = bc_manager.wallet_manager.get_wallet(address)
    except Exception as e:
        print(f"[ERREUR] {e}")
        return
    print(f"\n--- Détails de {address} ---")
    print(f"Disponible ({len(wallet.available_tokens)}): {wallet.available_tokens}")
    print(f"Staké ({len(wallet.staked_tokens)}):   {wallet.staked_tokens}")


def stacker_token(bc_manager, address):
    try:
        wallet = bc_manager.wallet_manager.get_wallet(address)
    except Exception as e:
        print(f"[ERREUR] {e}")
        return
    if not wallet.available_tokens:
        print("Aucun token disponible pour staking.")
        return
    print("\nMode de staking :")
    print("1. Staker par ID")
    print("2. Staking rapide (n premiers tokens)")
    mode = input("Choix du mode (1 ou 2, Entrée pour annuler): ").strip()
    if mode == '1':
        print("Tokens disponibles pour staking :")
        for t in wallet.available_tokens:
            print(f"  - {t}")
        token_id = input("ID du token à staker (vide pour annuler): ").strip()
        if not token_id:
            return
        try:
            bc_manager.stake_token(token_id, address)
            print(f"Staking initié pour token {token_id} (en attente de validation).")
        except Exception as e:
            print(f"[ERREUR] {e}")
    elif mode == '2':
        nb = input("Nombre de tokens à staker (vide pour annuler): ").strip()
        if not nb:
            return
        try:
            n = int(nb)
            to_stake = list(wallet.available_tokens)[:n]
            for token_id in to_stake:
                bc_manager.stake_token(token_id, address)
            print(f"Staking rapide initié pour tokens : {to_stake} (en attente de validation).")
        except ValueError:
            print("Nombre invalide.")
    else:
        print("Opération annulée ou mode invalide.")



def unstacker_token(bc_manager, address):
    try:
        wallet = bc_manager.wallet_manager.get_wallet(address)
    except Exception as e:
        print(f"[ERREUR] {e}")
        return
    if not wallet.staked_tokens:
        print("Aucun token staké disponible.")
        return
    print("\nMode de unstaking :")
    print("1. Unstaker par ID")
    print("2. Unstaking rapide (n premiers tokens)")
    mode = input("Choix du mode (1 ou 2, Entrée pour annuler): ").strip()
    if mode == '1':
        print("Tokens stakés disponibles :")
        for t in wallet.staked_tokens:
            print(f"  - {t}")
        token_id = input("ID du token à unstaker (vide pour annuler): ").strip()
        if not token_id:
            return
        try:
            bc_manager.unstake_token(token_id, address)
            print(f"Unstaking initié pour token {token_id} (en attente de validation).")
        except Exception as e:
            print(f"[ERREUR] {e}")
    elif mode == '2':
        nb = input("Nombre de tokens à unstaker (vide pour annuler): ").strip()
        if not nb:
            return
        try:
            n = int(nb)
            to_unstake = list(wallet.staked_tokens)[:n]
            for token_id in to_unstake:
                bc_manager.unstake_token(token_id, address)
            print(f"Unstaking rapide initié pour tokens : {to_unstake} (en attente de validation).")
        except ValueError:
            print("Nombre invalide.")
    else:
        print("Opération annulée ou mode invalide.")


def transferer_tokens(bc_manager, address):
    try:
        wallet = bc_manager.wallet_manager.get_wallet(address)
    except Exception as e:
        print(f"[ERREUR] {e}")
        return
    if not wallet.available_tokens:
        print("Aucun token disponible pour transfert.")
        return
    print("\nMode de transfert :")
    print("1. Transfert par ID")
    print("2. Transfert rapide (n premiers tokens)")
    mode = input("Choix du mode (1 ou 2, Entrée pour annuler): ").strip()
    tokens_to_transfer = []
    if mode == '1':
        print("Tokens disponibles pour transfert :")
        for t in wallet.available_tokens:
            print(f"  - {t}")
        token_id = input("ID du token à transférer (vide pour annuler): ").strip()
        if not token_id:
            return
        tokens_to_transfer = [token_id]
    elif mode == '2':
        nb = input("Nombre de tokens à transférer (vide pour annuler): ").strip()
        if not nb:
            return
        try:
            n = int(nb)
            tokens_to_transfer = list(wallet.available_tokens)[:n]
            print(f"Transfert rapide initié pour tokens : {tokens_to_transfer}")
        except ValueError:
            print("Nombre invalide.")
            return
    else:
        print("Opération annulée ou mode invalide.")
        return
    print("Wallets disponibles pour recevoir :")
    for w_addr, w_obj in bc_manager.wallet_manager.wallets.items():
        if w_addr != address:
            print(f"  - {w_addr} (available: {w_obj.balance()}, staked: {w_obj.staked_balance()})")
    dest = input("Adresse du wallet destinataire (vide pour annuler): ").strip()
    if not dest:
        return
    for token_id in tokens_to_transfer:
        try:
            bc_manager.transfer_token(token_id, address, dest)
            print(f"Transfert initié pour token {token_id} (en attente de validation).")
        except Exception as e:
            print(f"[ERREUR] {e}")

            
            
def load_scenario(bc_manager):
    print("\n--- Charger scénario de vote ---")
    print("1. Cas idéal (tous valident)")
    print("2. Cas réaliste (choix de nœuds malins)")
    print("3. Cas limite (validateur puissant)")
    mode = input("Choix du scénario: ").strip()
    bc_manager.manual_votes.clear()
    validators = bc_manager.validators
    if mode == '1':
        for v in validators: bc_manager.manual_votes[v] = True
        print("Scénario idéal chargé.")
    elif mode == '2':
        print("Liste validateurs :", validators)
        malins = input("Nœuds malins (séparés par une virgule: wallet1,wallet2) : ").split(',')
        for v in validators:
            bc_manager.manual_votes[v] = (v not in malins)
        print("Scénario réaliste chargé.")
    elif mode == '3':
        # choisir validateur le plus staké
        stakes = bc_manager.stakes
        if stakes:
            puissant = max(stakes, key=lambda x: stakes[x])
            for v in validators:
                bc_manager.manual_votes[v] = True
            bc_manager.manual_votes[puissant] = False
            print(f"Scénario limite : {puissant} malintentionné.")
        else:
            print("Aucun validateur pour scénario.")
    else:
        print("Scénario invalide.")


def simulate_fake_traffic(bc_manager):
    try:
        nb = int(input("Nombre de transactions factices: ").strip())
    except ValueError:
        print("Entrée invalide.")
        return

    wallets = list(bc_manager.wallet_manager.wallets.keys())
    executed = []

    for i in range(nb):
        src, dst = random.sample(wallets, 2)
        w_src = bc_manager.wallet_manager.get_wallet(src)
        if not w_src.available_tokens:
            # pas de token à transférer, on passe
            continue
        token_id = list(w_src.available_tokens)[0]
        # on lance la transaction et on récupère l'objet tx
        tx = bc_manager.transfer_token(token_id, src, dst)
        executed.append(tx)
        # on affiche tout de suite
        print(f"[{i+1}/{nb}] {src} → {dst} | token {token_id}")

    # Bilan
    print(f"\n🔹 {len(executed)} transactions factices exécutées sur {nb} tentatives.")
    if executed:
        print("Détails des transactions :")
        for tx in executed:
            action = tx.get("action")
            tid    = tx.get("token_id")
            frm    = tx.get("from")
            to     = tx.get("to")
            print(f"  - {action} : token {tid} de {frm} vers {to}")

def main():
    bc_manager = BlockchainManager(initial_supply=250, origin_wallet="wallet_creator")
    print("Blockchain initialisée.")
    while True:
        display_menu()
        choice = input("Choix: ").strip()
        if choice == '1':
            blockchain_menu(bc_manager)
        elif choice == '2':
            display_wallet_list(bc_manager)
            addr = input("Wallet (vide pour annuler): ").strip()
            display_wallet(bc_manager, addr)
        elif choice == '3':
            display_wallet_list(bc_manager)
            addr = input("Wallet (vide pour annuler): ").strip()
            if addr: stacker_token(bc_manager, addr)
        elif choice == '4':
            display_wallet_list(bc_manager)
            addr = input("Wallet (vide pour annuler): ").strip()
            if addr: unstacker_token(bc_manager, addr)
        elif choice == '5':
            display_wallet_list(bc_manager)
            addr = input("Wallet source (vide pour annuler): ").strip()
            if addr: transferer_tokens(bc_manager, addr)
        elif choice == '6':
            new_addr = input("Nouvel wallet (vide pour annuler): ").strip()
            if not new_addr:
                continue  # Annulation, retour au menu principal

            # Saisie du montant de tokens initiaux
            amount_str = input("Nombre de tokens initiaux à créditer (défaut 5) : ").strip()
            try:
                initial_credit = int(amount_str) if amount_str else 5
            except ValueError:
                print("Entrée invalide, utilisation de 5 tokens par défaut.")
                initial_credit = 5

            # Création du wallet
            try:
                bc_manager.create_wallet_for_user(new_addr, initial_credit=initial_credit)
                print(f"Wallet '{new_addr}' créé avec {initial_credit} token(s).")
            except Exception as e:
                print(f"[ERREUR] {e}")

        elif choice == '7':
            load_scenario(bc_manager)
        elif choice == '8':
            simulate_fake_traffic(bc_manager)
        elif choice == '9':
            break
        else:
            print("Choix invalide.")



if __name__ == "__main__":
    main()
