import socket
import threading
import json
import time
from src.blockchain_manager import BlockchainManager

# -----------------------------------------------------
# 1. Fonctions pour le serveur TCP (réception de messages)
# -----------------------------------------------------
def handle_client(conn, addr):
    """Gère les connexions entrantes sur un nœud en recevant et décodant les messages JSON."""
    print(f"[INFO] Connexion entrante de {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                message = json.loads(data.decode())
                print(f"[REÇU] Message de {addr}: {message}")
                # Vous pouvez ici ajouter le traitement selon le type de message
            except json.JSONDecodeError:
                print("[ERREUR] Erreur lors du décodage du message JSON.")
    except Exception as e:
        print(f"[ERREUR] Exception lors de la gestion de {addr}: {e}")
    finally:
        conn.close()

def start_server(host='0.0.0.0', port=5000):
    """Démarre le serveur TCP qui écoute et décode les connexions entrantes."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[INFO] Serveur TCP démarré sur {host}:{port}")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# -----------------------------------------------------
# 2. Fonctions pour le client TCP (envoi de messages)
# -----------------------------------------------------
def send_message(peer_ip, peer_port, message):
    """Envoie un message JSON à un pair via TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((peer_ip, peer_port))
            client_socket.sendall(json.dumps(message).encode())
            print(f"[INFO] Message envoyé à {peer_ip}:{peer_port}")
        except Exception as e:
            print(f"[ERREUR] Impossible de se connecter à {peer_ip}:{peer_port} - {e}")

# -----------------------------------------------------
# 3. Fonctions d'interaction via le menu
# -----------------------------------------------------
def display_node_status(bc_manager):
    """Affiche quelques informations sur l'état actuel du nœud."""
    print("\n--- Statut du nœud ---")
    print(f"Hauteur de la blockchain : {len(bc_manager.chain)}")
    print("Transactions en attente :")
    if bc_manager.pending_transactions:
        for tx in bc_manager.pending_transactions:
            print(f"  - {tx}")
    else:
        print("  Aucune transaction en attente.")
    print("-------------------------\n")

def sync_with_network():
    """
    Stub pour la synchronisation avec le réseau.
    L'idée est de se connecter à un ou plusieurs pairs pour récupérer et comparer la blockchain.
    Vous pourrez compléter cette fonction ultérieurement.
    """
    print("Synchronisation avec le réseau en cours ...")
    time.sleep(1)
    print("Synchronisation terminée (fonction à développer).")

# -----------------------------------------------------
# 4. Menu principal
# -----------------------------------------------------
def main_menu():
    # Instanciation du gestionnaire de blockchain
    bc_manager = BlockchainManager(initial_supply=100, origin_wallet="wallet_creator")
    
    # Lancement du serveur TCP dans un thread séparé pour écouter en permanence
    server_thread = threading.Thread(target=start_server, args=('0.0.0.0', 5000), daemon=True)
    server_thread.start()
    
    while True:
        print("\n--- MENU ---")
        print("1. Afficher le statut du nœud")
        print("2. Connecter à un pair")
        print("3. Créer une transaction")
        print("4. Staker un token")
        print("5. Unstaker un token")
        print("6. Synchroniser avec le réseau")
        print("7. Quitter")
        print("------------")
        choix = input("Votre choix : ").strip()
        
        if choix == '1':
            display_node_status(bc_manager)
        elif choix == '2':
            peer_ip = input("Entrez l'IP du pair : ").strip()
            try:
                peer_port = int(input("Entrez le port du pair : ").strip())
            except ValueError:
                print("Port invalide !")
                continue
            # Ici, nous envoyons un message de ping pour tester la connexion.
            msg = {"type": "ping", "data": "Bonjour, je suis un nœud !"}
            send_message(peer_ip, peer_port, msg)
        elif choix == '3':
            print("=== Création d'une transaction ===")
            from_wallet = input("Entrez l'adresse de l'émetteur : ").strip()
            to_wallet = input("Entrez l'adresse du destinataire : ").strip()
            token_id = input("Entrez l'ID du token à transférer : ").strip()
            try:
                bc_manager.transfer_token(token_id, from_wallet, to_wallet)
                print("Transaction créée et ajoutée aux transactions en attente.")
            except Exception as e:
                print(f"[ERREUR] {e}")
        elif choix == '4':
            print("=== Staking d'un token ===")
            address = input("Entrez l'adresse du wallet à staker : ").strip()
            token_id = input("Entrez l'ID du token à staker : ").strip()
            try:
                bc_manager.stake_token(token_id, address)
                print("Token staké avec succès.")
            except Exception as e:
                print(f"[ERREUR] {e}")
        elif choix == '5':
            print("=== Unstaking d'un token ===")
            address = input("Entrez l'adresse du wallet à unstaker : ").strip()
            token_id = input("Entrez l'ID du token à unstaker : ").strip()
            try:
                bc_manager.unstake_token(token_id, address)
                print("Token unstaké avec succès.")
            except Exception as e:
                print(f"[ERREUR] {e}")
        elif choix == '6':
            sync_with_network()
        elif choix == '7':
            print("Au revoir.")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    main_menu()