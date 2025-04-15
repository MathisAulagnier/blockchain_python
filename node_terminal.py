import argparse
import socket
import threading
import json
import time
from src.blockchain_manager import BlockchainManager

# -------------------------------
# Partie serveur TCP pour le nœud
# -------------------------------
def handle_client(conn, addr):
    """Traite les connexions entrantes et affiche les messages reçus."""
    print(f"[INFO] Connexion entrante de {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                message = json.loads(data.decode())
                print(f"[REÇU] {addr} => {message}")
                # Vous pouvez ajouter ici des traitements spécifiques selon le type de message
            except json.JSONDecodeError:
                print("[ERREUR] Impossible de décoder le message JSON.")
    except Exception as e:
        print(f"[ERREUR] Exception durant la réception depuis {addr}: {e}")
    finally:
        conn.close()

def start_server(host, port):
    """Démarre un serveur TCP pour écouter les messages entrants."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[INFO] Serveur TCP démarré sur {host}:{port}")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def send_message(peer_ip, peer_port, message):
    """Envoie un message JSON à un pair."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((peer_ip, peer_port))
            sock.sendall(json.dumps(message).encode())
            print(f"[INFO] Message envoyé à {peer_ip}:{peer_port}")
        except Exception as e:
            print(f"[ERREUR] Échec de connexion à {peer_ip}:{peer_port} => {e}")

# -------------------------------
# Menu interactif du nœud
# -------------------------------
def display_menu():
    print("\n--- MENU ---")
    print("1. Afficher le statut du nœud")
    print("2. Envoyer un message à un pair")
    print("3. Afficher l'état du wallet")
    print("4. Synchroniser la blockchain (stub)")
    print("5. Stacker un token (stub)") # Affihcage de la liste des tokens disponibles
    print("6. Unstacker un token (stub)") # Affihcage de la liste des tokens disponibles
    print("7. Transférer un token (stub)") # Afficher la liste des wallets disponibles
    print("9. Quitter")
    print("------------")


def display_status(bc_manager):
    """Affiche quelques informations sur le nœud."""
    print("\n--- Statut du nœud ---")
    print(f"Hauteur de la blockchain : {len(bc_manager.chain)}")
    print("Transactions en attente:")
    if bc_manager.pending_transactions:
        for tx in bc_manager.pending_transactions:
            print(f"  - {tx}")
    else:
        print("  Aucune transaction en attente.")
    print("------------------------\n")

def display_wallet(bc_manager, node_id):
    try:
        wallet = bc_manager.wallet_manager.get_wallet(node_id)
        print(f"\nWallet {node_id} -> {wallet}")
        if wallet.available_tokens:
            print("Tokens disponibles:")
            for token in wallet.available_tokens:
                print(f"  - {token}")
        else:
            print("Aucun token disponible.")
        if wallet.staked_tokens:
            print("Tokens stakés:")
            for token in wallet.staked_tokens:
                print(f"  - {token}")
        else:
            print("Aucun token staké.")
    except Exception as e:
        print(f"[ERREUR] {e}")

def stacker_token(bc_manager, node_id):
    wallet = bc_manager.wallet_manager.get_wallet(node_id)
    if wallet.available_tokens:
        print("Tokens disponibles pour staking:")
        for token in wallet.available_tokens:
            print(f"  - {token}")
        token_id = input("Entrez l'ID du token à staker: ").strip()
        try:
            bc_manager.stake_token(token_id, node_id)
            print(f"Token {token_id} staké par {node_id}.")
        except Exception as e:
            print(f"[ERREUR] {e}")
    else:
        print("Aucun token disponible pour staker.")

def unstacker_token(bc_manager, node_id):
    wallet = bc_manager.wallet_manager.get_wallet(node_id)
    if wallet.staked_tokens:
        print("Tokens stakés disponibles:")
        for token in wallet.staked_tokens:
            print(f"  - {token}")
        token_id = input("Entrez l'ID du token à unstaker: ").strip()
        try:
            bc_manager.unstake_token(token_id, node_id)
            print(f"Token {token_id} unstaké par {node_id}.")
        except Exception as e:
            print(f"[ERREUR] {e}")
    else:
        print("Aucun token staké disponible pour unstaker.")

def transferer_token(bc_manager, node_id):
    wallet = bc_manager.wallet_manager.get_wallet(node_id)
    if wallet.available_tokens:
        print("Tokens disponibles pour transfert:")
        for token in wallet.available_tokens:
            print(f"  - {token}")
        token_id = input("Entrez l'ID du token à transférer: ").strip()
    else:
        print("Aucun token disponible pour transfert.")
        return

    # Affichage des autres wallets enregistrés
    print("Wallets disponibles pour recevoir un transfert:")
    for w_id in bc_manager.wallet_manager.wallets.keys():
        if w_id != node_id:
            print(f"  - {w_id}")
    dest = input("Entrez l'adresse du wallet destinataire: ").strip()
    try:
        bc_manager.transfer_token(token_id, node_id, dest)
        print(f"Token {token_id} transféré de {node_id} vers {dest}.")
    except Exception as e:
        print(f"[ERREUR] {e}")


def sync_blockchain():
    """Fonction stub pour synchroniser la blockchain avec des pairs."""
    print("Synchronisation en cours... (fonction à développer)")
    time.sleep(1)
    print("Synchronisation terminée.")

# -------------------------------
# Programme principal
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Nœud de la blockchain décentralisée.")
    parser.add_argument("--id", type=str, required=True, help="Identifiant du nœud (ex: node1)")
    parser.add_argument("--port", type=int, required=True, help="Port d'écoute du nœud")
    parser.add_argument("--peers", type=str, default="", help="Liste des pairs au format ip:port, séparés par des virgules")
    args = parser.parse_args()

    node_id = args.id
    host = "0.0.0.0"
    port = args.port
    peers = []
    if args.peers:
        for peer in args.peers.split(","):
            ip, p = peer.split(":")
            peers.append((ip.strip(), int(p.strip())))

    # Initialisation de la blockchain et distribution initiale
    # Conserver l'initialisation avec les wallets Lina, JJ et Mathis
    bc_manager = BlockchainManager(initial_supply=100, origin_wallet="wallet_creator", transaction_threshold=2)
    
    # Par défaut, l'initialisation de la blockchain crée aussi les wallets Lina, JJ et Mathis.
    # Ici, nous supposons que chaque nœud s'identifie par son node_id, qui correspond à un wallet existant
    try:
        bc_manager.wallet_manager.get_wallet(node_id)
        print(f"Le wallet '{node_id}' existe déjà.")
    except ValueError:
        # Si le wallet n'existe pas, on peut le créer (choix à adapter selon votre logique)
        try:
            bc_manager.create_wallet_for_user(node_id, initial_credit=10)
            print(f"Wallet '{node_id}' créé et crédité avec 10 tokens.")
        except Exception as e:
            print(f"[ERREUR] Création du wallet '{node_id}': {e}")

    # Démarrer le serveur TCP pour permettre la communication avec les pairs
    server_thread = threading.Thread(target=start_server, args=(host, port), daemon=True)
    server_thread.start()

    # Boucle du menu interactif
    while True:
        display_menu()
        choix = input("Votre choix : ").strip()
        if choix == "1":
            display_status(bc_manager)
        elif choix == "2":
            peer_ip = input("Entrez l'IP du pair : ").strip()
            try:
                peer_port = int(input("Entrez le port du pair : ").strip())
            except ValueError:
                print("Port invalide")
                continue
            message = {
                "type": "ping",
                "data": f"Bonjour du nœud {node_id}"
            }
            send_message(peer_ip, peer_port, message)
        elif choix == "3":
            display_wallet(bc_manager, node_id)
        elif choix == "4":
            sync_blockchain()
        elif choix == "5":
            stacker_token(bc_manager, node_id)
        elif choix == "6":
            unstacker_token(bc_manager, node_id)
        elif choix == "7":
            transferer_token(bc_manager, node_id)
        elif choix == "9":
            print("Au revoir.")
            break
        else:
            print("Choix invalide, réessayez.")

if __name__ == "__main__":
    main()