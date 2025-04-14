import socket
import threading
import json
import uuid
import time
import os
import queue # Pour communiquer entre le thread d'écoute et le thread principal
from common_socket_utils import send_message, receive_message # Import des utilitaires

# --- Configuration ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001 # Doit correspondre au port du serveur socket
WALLET_FILE = "my_wallet.json"

# --- État Global Client (simplifié) ---
client_socket = None
my_wallet_address = None
server_messages_queue = queue.Queue() # File pour les messages reçus du serveur

# --- Gestion du Wallet Client ---
def load_or_create_wallet():
    """Charge ou crée le wallet localement."""
    # (Identique à la version précédente)
    if os.path.exists(WALLET_FILE):
        try:
            with open(WALLET_FILE, 'r') as f:
                wallet_data = json.load(f)
                print(f"Wallet chargé depuis {WALLET_FILE}: {wallet_data['address']}")
                return wallet_data['address']
        except Exception as e:
            print(f"Erreur en lisant {WALLET_FILE}: {e}. Création d'un nouveau wallet.")
    new_address = str(uuid.uuid4())
    wallet_data = {"address": new_address}
    try:
        with open(WALLET_FILE, 'w') as f: json.dump(wallet_data, f)
        print(f"Nouveau wallet créé et sauvegardé dans {WALLET_FILE}: {new_address}")
        return new_address
    except Exception as e:
        print(f"ERREUR: Impossible de sauvegarder le nouveau wallet dans {WALLET_FILE}: {e}")
        return new_address # Retourne quand même pour la session

# --- Connexion et Enregistrement ---
def connect_to_server():
    """Établit la connexion socket avec le serveur."""
    global client_socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"[Client] Connecté au serveur {SERVER_HOST}:{SERVER_PORT}")
        client_socket = sock
        return True
    except ConnectionRefusedError:
        print(f"Erreur: Connexion refusée. Le serveur est-il lancé sur {SERVER_HOST}:{SERVER_PORT}?")
        return False
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

def register_with_server(wallet_addr):
    """Envoie la requête d'enregistrement au serveur."""
    if not client_socket: return False
    payload = {"action": "register", "address": wallet_addr}
    if send_message(client_socket, payload):
        response = receive_message(client_socket)
        if response and response.get("status") == "ok":
            print(f"[Client] Enregistrement réussi: {response.get('message')}")
            return True
        else:
            error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
            print(f"[Client] Échec de l'enregistrement: {error_msg}")
            return False
    else:
        print("[Client] Échec de l'envoi de la requête d'enregistrement.")
        return False

# --- Thread d'Écoute des Messages Serveur ---
def listen_to_server(sock):
    """Thread qui écoute en continu les messages venant du serveur."""
    while True:
        try:
            message = receive_message(sock)
            if message is None:
                print("[Listener] Connexion serveur perdue ou message invalide. Arrêt du listener.")
                # Option: Mettre un message spécial dans la queue pour signaler au main thread
                server_messages_queue.put({"action": "server_disconnected"})
                break
            # Mettre le message reçu dans la file pour traitement par le thread principal
            # print(f"[Listener] Message reçu du serveur: {message}") # Debug
            server_messages_queue.put(message)
        except Exception as e:
            print(f"[Listener] Erreur dans le thread d'écoute: {e}")
            server_messages_queue.put({"action": "listener_error"})
            break # Arrêter le thread en cas d'erreur majeure
    print("[Listener] Thread d'écoute terminé.")


# --- Fonctions d'Interaction Client (adaptées pour socket) ---

def send_request_and_get_response(payload):
    """Envoie une requête et attend la réponse directe."""
    if not client_socket:
        print("Erreur: Pas connecté au serveur.")
        return None
    if send_message(client_socket, payload):
        response = receive_message(client_socket)
        return response
    else:
        print("Erreur lors de l'envoi de la requête.")
        return None

def get_balance(wallet_addr):
    print("\n--- Récupération du Solde ---")
    payload = {"action": "get_wallet_info", "address": wallet_addr}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        data = response.get("data", {})
        print(f"  Adresse: {data.get('address')}")
        print(f"  Solde Disponible: {data.get('available_balance', 'N/A')} tokens")
        print(f"  Solde Staké: {data.get('staked_balance', 'N/A')} tokens")
        print(f"  Solde Total: {data.get('total_balance', 'N/A')} tokens")
        # ... (affichage détaillé des tokens comme avant) ...
    else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
    print("----------------------------\n")

def get_tokens(wallet_addr, token_type='available'):
    """Helper pour récupérer les IDs de tokens dispo ou stakés."""
    payload = {"action": "get_wallet_info", "address": wallet_addr}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        data = response.get("data", {})
        key = 'available_tokens' if token_type == 'available' else 'staked_tokens'
        return data.get(key, [])
    return []

def transfer_tokens(wallet_addr):
    print("\n--- Transfert de Token ---")
    recipient_address = input("Adresse du destinataire : ")
    if not recipient_address: print("Adresse invalide."); return

    available_tokens = get_tokens(wallet_addr, 'available')
    if not available_tokens: print("Aucun token disponible."); return
    # ... (logique de choix du token identique à avant) ...
    try:
         # ... (choix du token_to_transfer) ...
         choice = int(input(f"Entrez le numéro du token à transférer (0-{len(available_tokens)-1}) : ")) # Reprendre logique choix
         if not (0 <= choice < len(available_tokens)): print("Choix invalide."); return
         token_to_transfer = available_tokens[choice]
    except ValueError: print("Entrée invalide."); return

    print(f"Transfert de {token_to_transfer[:8]}... vers {recipient_address}...")
    payload = {"action": "transfer", "to_address": recipient_address, "token_id": token_to_transfer}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        print(f"Succès: {response.get('message')}")
    else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
    print("------------------------\n")


def stake_token(wallet_addr):
    print("\n--- Staker un Token ---")
    available_tokens = get_tokens(wallet_addr, 'available')
    if not available_tokens: print("Aucun token disponible pour stake."); return
    # ... (logique de choix du token identique à avant) ...
    try:
        # ... (choix du token_to_stake) ...
        choice = int(input(f"Entrez le numéro du token à staker (0-{len(available_tokens)-1}) : ")) # Reprendre logique choix
        if not (0 <= choice < len(available_tokens)): print("Choix invalide."); return
        token_to_stake = available_tokens[choice]
    except ValueError: print("Entrée invalide."); return

    print(f"Staking du token {token_to_stake[:8]}...")
    payload = {"action": "stake", "token_id": token_to_stake}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        print(f"Succès: {response.get('message')}")
    else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
    print("---------------------\n")


def unstake_token(wallet_addr):
    print("\n--- Unstaker un Token ---")
    staked_tokens = get_tokens(wallet_addr, 'staked')
    if not staked_tokens: print("Aucun token staké."); return
    # ... (logique de choix du token identique à avant) ...
    try:
        # ... (choix du token_to_unstake) ...
        choice = int(input(f"Entrez le numéro du token à unstaker (0-{len(staked_tokens)-1}) : ")) # Reprendre logique choix
        if not (0 <= choice < len(staked_tokens)): print("Choix invalide."); return
        token_to_unstake = staked_tokens[choice]
    except ValueError: print("Entrée invalide."); return

    print(f"Unstaking du token {token_to_unstake[:8]}...")
    payload = {"action": "unstake", "token_id": token_to_unstake}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        print(f"Succès: {response.get('message')}")
    else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
    print("-----------------------\n")


def view_blocks():
    print(f"\n--- Derniers Blocs ---")
    payload = {"action": "get_blocks", "limit": 5}
    response = send_request_and_get_response(payload)
    if response and response.get("status") == "ok":
        blocks = response.get("data", [])
        if not blocks: print(" Aucun bloc trouvé.")
        for block in reversed(blocks): # Afficher du plus récent au plus ancien
             print(f"  Bloc #{block['index']} (Hash: {block['hash'][:10]}...)")
             # ... (affichage identique à avant) ...
             print(f"    Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block['timestamp']))}")
             print(f"    Validateur: {block['validator']}")
             print(f"    Transactions: {block['transaction_count']}")
             print("-" * 10)
    else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
    print("--------------------\n")


def view_validators():
     print("\n--- Validateurs Actuels ---")
     payload = {"action": "get_validators"}
     response = send_request_and_get_response(payload)
     if response and response.get("status") == "ok":
        data = response.get("data", {})
        stakes = data.get('stakes', {})
        if not stakes: print("  Aucun validateur actif.")
        else:
             for validator, stake in stakes.items():
                  print(f"  - {validator}: {stake} token(s) staké(s)")
     else:
        error_msg = response.get('error', 'Réponse invalide') if response else 'Pas de réponse'
        print(f"Erreur: {error_msg}")
     print("-------------------------\n")

# --- Traitement des Messages Serveur Reçus Asynchronement ---
def process_server_messages():
    """Vérifie la queue et traite les messages non-bloquants du serveur."""
    try:
        while not server_messages_queue.empty():
            message = server_messages_queue.get_nowait()
            action = message.get("action")
            print(f"\n[Notification Serveur] Action: {action}") # Debug

            if action == "server_disconnected":
                print("!!! Connexion au serveur perdue. Veuillez redémarrer le client. !!!")
                # Ici, on pourrait vouloir quitter ou tenter de reconnecter
                global client_socket
                if client_socket: client_socket.close(); client_socket = None
                return False # Signale au main loop d'arrêter

            elif action == "listener_error":
                 print("!!! Erreur critique dans le listener serveur. !!!")
                 return False # Arrêter

            elif action == "request_vote":
                # Le serveur demande un vote !
                block_index = message.get("block_index")
                block_hash = message.get("block_hash", "N/A")[:10]
                transactions_summary = message.get("transactions", []) # Le serveur devrait envoyer un résumé
                print("\n=== ! DEMANDE DE VOTE ! ===")
                print(f"Le serveur demande votre vote pour le bloc candidat #{block_index} (Hash: {block_hash}...)")
                print("Transactions incluses (résumé):")
                # Afficher un résumé lisible des transactions
                for tx in transactions_summary: print(f"  - {tx}") # Le serveur doit formater ça
                while True:
                    vote_input = input("Approuver ce bloc? (oui/non) : ").lower()
                    if vote_input == 'oui':
                        vote = True; break
                    elif vote_input == 'non':
                        vote = False; break
                    else: print("Réponse invalide.")
                # Envoyer la réponse au serveur
                vote_payload = {"action": "submit_vote", "block_index": block_index, "vote": vote}
                send_request_and_get_response(vote_payload) # On ignore la réponse ici pour l'instant
                print("===========================\n")

            elif action == "new_block_notification":
                 block_index = message.get("block_index", "N/A")
                 block_hash = message.get("block_hash", "N/A")[:10]
                 validator = message.get("validator", "N/A")
                 print(f"-> Nouveau bloc #{block_index} ajouté par {validator} (Hash: {block_hash}...)")

            else:
                print(f"  Message serveur non traité: {message}")

            server_messages_queue.task_done() # Marquer la tâche comme terminée
    except queue.Empty:
        pass # Normal s'il n'y a pas de message
    return True # Continue la boucle principale

# --- Boucle Principale du Client ---
def main_loop(wallet_addr):
    global my_wallet_address
    my_wallet_address = wallet_addr # Assigner pour que les fonctions l'utilisent

    # Démarrer le thread d'écoute
    if client_socket:
        listener_thread = threading.Thread(target=listen_to_server, args=(client_socket,), daemon=True)
        listener_thread.start()
    else:
        print("Impossible de démarrer le listener: non connecté.")
        return

    while True:
        # 1. Traiter les messages asynchrones du serveur
        if not process_server_messages():
             break # Arrêter si process_server_messages signale une erreur

        # 2. Afficher le menu et attendre l'input utilisateur
        print("\n=== Menu Principal (Socket) ===")
        print(f" Wallet: {my_wallet_address}")
        print("1. Voir solde")
        print("2. Transférer")
        print("3. Staker")
        print("4. Unstaker")
        print("5. Voir blocs")
        print("6. Voir validateurs")
        print("0. Quitter")

        choice = input("Votre choix : ")

        if choice == '1': get_balance(my_wallet_address)
        elif choice == '2': transfer_tokens(my_wallet_address)
        elif choice == '3': stake_token(my_wallet_address)
        elif choice == '4': unstake_token(my_wallet_address)
        elif choice == '5': view_blocks()
        elif choice == '6': view_validators()
        elif choice == '0':
            print("Déconnexion..."); break
        else: print("Choix invalide.")

        time.sleep(0.1) # Petite pause pour éviter de surcharger le CPU

    # Nettoyage
    if client_socket:
        print("Fermeture de la connexion.")
        try:
             client_socket.close()
        except: pass


# --- Point d'Entrée Client ---
if __name__ == "__main__":
    my_addr = load_or_create_wallet()
    if not my_addr:
        print("Impossible de déterminer l'adresse du wallet. Arrêt.")
    else:
        if connect_to_server():
            if register_with_server(my_addr):
                 print("[Client] Prêt à interagir.")
                 main_loop(my_addr) # Lance la boucle principale
            else:
                 print("[Client] Échec de l'enregistrement. Arrêt.")
            # Fermeture propre si on sort de main_loop sans erreur majeure
            if client_socket:
                 try: client_socket.close()
                 except: pass
        else:
            print("[Client] Impossible de se connecter au serveur. Arrêt.")