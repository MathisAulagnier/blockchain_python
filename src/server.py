# server.py (Version Socket)
import socket
import threading
import json
import time
from src.blockchain_manager import BlockchainManager
from common_socket_utils import send_message, receive_message # Import des utilitaires

# --- Configuration ---
HOST = '127.0.0.1'
PORT = 5001 # Port différent de la version Flask pour éviter conflit
INITIAL_TOKENS_PER_USER = 10
MAX_CLIENTS = 10

# --- Initialisation Blockchain ---
# Assurez-vous que BlockchainManager est modifié comme dans l'étape précédente
blockchain_manager = BlockchainManager(initial_supply=1000, origin_wallet="wallet_server_origin", transaction_threshold=5)
print(f"Blockchain Manager initialisé pour {blockchain_manager.origin_wallet}.")
print(f"Seuil de transaction pour commit auto: {blockchain_manager.transaction_threshold}")

# --- Gestion des Clients Connectés et Verrous ---
clients = {} # Dictionnaire {client_socket: wallet_address} (ou l'inverse ?) Mieux: {wallet_address: client_socket}
clients_lock = threading.Lock() # Verrou pour accéder/modifier le dict clients
state_lock = threading.Lock() # Verrou pour accéder/modifier BlockchainManager

# --- Logique de Commit / Vote (Simplifiée pour l'instant) ---
# TODO: Adapter initiate_pbft_consensus pour envoyer/recevoir via socket

# --- Gestionnaire de Client (Thread) ---
def handle_client(client_socket, client_address):
    """Gère la communication avec un client connecté dans un thread dédié."""
    print(f"[Server] Nouvelle connexion de {client_address}")
    current_wallet_address = None # Le client doit s'enregistrer

    try:
        while True:
            # Recevoir un message du client
            request_data = receive_message(client_socket)
            if request_data is None:
                # Erreur de réception ou connexion fermée
                print(f"[Server] Connexion perdue ou message invalide de {client_address}")
                break

            action = request_data.get('action')
            print(f"[Server] Requête reçue de {current_wallet_address or client_address}: Action='{action}'")

            response_data = {"status": "error", "error": "Action inconnue ou requête invalide"}

            # --- Traitement des Actions ---
            if action == 'register':
                address = request_data.get('address')
                if address:
                    with state_lock:
                        try:
                            wallet = blockchain_manager.create_wallet_for_user(address, INITIAL_TOKENS_PER_USER)
                            current_wallet_address = address
                            # Stocker la connexion associée à cette adresse
                            with clients_lock:
                                clients[address] = client_socket
                            print(f"[Server] Client {client_address} enregistré comme Wallet {address}")
                            response_data = {"status": "ok", "message": f"Wallet {address} enregistré/trouvé."}
                            # Vérifier commit threshold APRES enregistrement (transferts initiaux)
                            # check_commit_threshold() # Attention, state_lock déjà pris? A appeler dehors
                        except ValueError as e:
                            response_data = {"status": "error", "error": str(e)}
                        except Exception as e:
                             response_data = {"status": "error", "error": f"Erreur interne: {e}"}
                    # Vérifier le seuil hors du lock principal si possible, sinon attention aux deadlocks
                    if response_data["status"] == "ok":
                         with state_lock: check_commit_threshold()

                else:
                    response_data = {"status": "error", "error": "Adresse manquante pour l'enregistrement"}

            # --- Actions nécessitant que le client soit enregistré ---
            elif current_wallet_address:
                 # ----- Get Wallet Info -----
                 if action == 'get_wallet_info':
                      addr_to_check = request_data.get('address', current_wallet_address) # Vérifie son propre wallet par défaut
                      try:
                           wallet = blockchain_manager.wallet_manager.get_wallet(addr_to_check)
                           info = {
                               "address": addr_to_check,
                               "available_balance": wallet.balance(),
                               "staked_balance": wallet.staked_balance(),
                               "total_balance": wallet.total_balance(),
                               "available_tokens": list(wallet.available_tokens),
                               "staked_tokens": list(wallet.staked_tokens)
                           }
                           response_data = {"status": "ok", "data": info}
                      except ValueError:
                           response_data = {"status": "error", "error": f"Wallet {addr_to_check} non trouvé"}
                      except Exception as e:
                          response_data = {"status": "error", "error": f"Erreur interne: {e}"}

                 # ----- Transfer -----
                 elif action == 'transfer':
                     req_fields = ['to_address', 'token_id']
                     if all(field in request_data for field in req_fields):
                          with state_lock:
                              try:
                                   sender_wallet = blockchain_manager.wallet_manager.get_wallet(current_wallet_address)
                                   token_id = request_data['token_id']
                                   if token_id not in sender_wallet.available_tokens:
                                       raise ValueError(f"Token {token_id[:8]} non dispo.")
                                   tx = blockchain_manager.transfer_token(token_id, current_wallet_address, request_data['to_address'])
                                   response_data = {"status": "ok", "message": "Transaction ajoutée", "transaction": tx}
                                   check_commit_threshold() # Vérif dans le lock
                              except ValueError as e:
                                   response_data = {"status": "error", "error": str(e)}
                              except Exception as e:
                                   response_data = {"status": "error", "error": f"Erreur interne: {e}"}
                     else: response_data = {"status": "error", "error": "Données manquantes (to_address, token_id)"}

                 # ----- Stake -----
                 elif action == 'stake':
                     token_id = request_data.get('token_id')
                     if token_id:
                          with state_lock:
                              try:
                                   wallet = blockchain_manager.wallet_manager.get_wallet(current_wallet_address)
                                   if token_id not in wallet.available_tokens:
                                        raise ValueError(f"Token {token_id[:8]} non dispo pour stake.")
                                   tx = blockchain_manager.stake_token(token_id, current_wallet_address)
                                   response_data = {"status": "ok", "message": "Stake ajouté", "transaction": tx}
                                   check_commit_threshold() # Vérif dans le lock
                              except ValueError as e:
                                   response_data = {"status": "error", "error": str(e)}
                              except Exception as e:
                                   response_data = {"status": "error", "error": f"Erreur interne: {e}"}
                     else: response_data = {"status": "error", "error": "Données manquantes (token_id)"}

                 # ----- Unstake -----
                 elif action == 'unstake':
                     token_id = request_data.get('token_id')
                     if token_id:
                          with state_lock:
                              try:
                                   wallet = blockchain_manager.wallet_manager.get_wallet(current_wallet_address)
                                   if token_id not in wallet.staked_tokens:
                                        raise ValueError(f"Token {token_id[:8]} non staké.")
                                   tx = blockchain_manager.unstake_token(token_id, current_wallet_address)
                                   response_data = {"status": "ok", "message": "Unstake ajouté", "transaction": tx}
                                   # TODO: Gérer la diminution du stake/validateur
                                   check_commit_threshold() # Vérif dans le lock
                              except ValueError as e:
                                   response_data = {"status": "error", "error": str(e)}
                              except Exception as e:
                                   response_data = {"status": "error", "error": f"Erreur interne: {e}"}
                     else: response_data = {"status": "error", "error": "Données manquantes (token_id)"}

                 # ----- Get Blocks -----
                 elif action == 'get_blocks':
                     limit = request_data.get('limit', 5)
                     try:
                          with state_lock: # Accès à la chain
                               chain_copy = list(blockchain_manager.chain)
                          blocks_to_return = chain_copy[-limit:]
                          blocks_json = [{
                               "index": b.index, "timestamp": b.timestamp, "previous_hash": b.previous_hash,
                               "hash": b.hash, "validator": b.validator, "pbft_signature": b.pbft_signature,
                               "transaction_count": len(b.transactions), "transactions": b.transactions
                           } for b in blocks_to_return]
                          response_data = {"status": "ok", "data": blocks_json}
                     except Exception as e:
                          response_data = {"status": "error", "error": f"Erreur interne: {e}"}

                 # ----- Get Validators -----
                 elif action == 'get_validators':
                      try:
                           with state_lock: # Accès aux validateurs/stakes
                               validators_info = {
                                   "validators": list(blockchain_manager.validators),
                                   "stakes": dict(blockchain_manager.stakes)
                               }
                           response_data = {"status": "ok", "data": validators_info}
                      except Exception as e:
                           response_data = {"status": "error", "error": f"Erreur interne: {e}"}

                 # ----- Submit Vote -----
                 elif action == 'submit_vote':
                      # Logique de réception de vote (sera appelée par initiate_pbft)
                      # ... (Implémentation future quand initiate_pbft sera adapté) ...
                      response_data = {"status": "ok", "message": "Vote reçu (traitement à faire)"}


            # --- Si action inconnue ou client non enregistré pour action protégée ---
            else:
                 if not current_wallet_address:
                     response_data = {"status": "error", "error": "Client non enregistré. Veuillez envoyer l'action 'register'."}
                 # else: action inconnue déjà géré par défaut

            # Envoyer la réponse au client
            if not send_message(client_socket, response_data):
                print(f"[Server] Échec de l'envoi de la réponse à {client_address}. Fermeture.")
                break # Sortir de la boucle si l'envoi échoue

    except ConnectionResetError:
        print(f"[Server] Connexion réinitialisée par {client_address}")
    except Exception as e:
        print(f"[Server] Erreur inattendue avec le client {client_address}: {e}")
    finally:
        # Nettoyage lors de la déconnexion du client
        print(f"[Server] Fermeture de la connexion avec {client_address}")
        with clients_lock:
            # Retirer le client du dictionnaire s'il était enregistré
            if current_wallet_address and current_wallet_address in clients:
                del clients[current_wallet_address]
        try:
             client_socket.close()
        except:
             pass # Socket peut-être déjà fermé

# --- Fonction pour vérifier et lancer le commit ---
# (Doit être appelée DANS un contexte où state_lock est détenu)
def check_commit_threshold():
    """Vérifie et lance le commit si seuil atteint."""
    if len(blockchain_manager.pending_transactions) >= blockchain_manager.transaction_threshold:
        print(f"[Server] Seuil de {blockchain_manager.transaction_threshold} transactions atteint. Lancement du commit...")
        # initiate_pbft_consensus() # Doit être adapté pour socket
        print("[Server] --- ATTENTION: La logique PBFT/Vote via socket n'est pas encore implémentée ---")
        # Simulation temporaire de l'ancien commit pour débloquer:
        try:
             blockchain_manager.commit_pending_transactions() # Utilise encore decide_vote() interne
        except Exception as e:
             print(f"[Server] Erreur lors du commit (simulé): {e}")


# --- Boucle Principale du Serveur ---
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permet de réutiliser l'adresse immédiatement après arrêt (utile en dev)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
    except OSError as e:
        print(f"Erreur de bind sur {HOST}:{PORT} - {e}. Le port est-il déjà utilisé?")
        return

    server_socket.listen(MAX_CLIENTS)
    print(f"*** Serveur Socket démarré et en écoute sur {HOST}:{PORT} ***")

    try:
        while True:
            # Accepter une nouvelle connexion
            client_socket, client_address = server_socket.accept()
            # Créer et démarrer un thread pour gérer ce client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[Server] Arrêt demandé par l'utilisateur.")
    finally:
        print("[Server] Fermeture du socket serveur.")
        server_socket.close()
        # Optionnel: tenter de notifier les clients restants
        # ...

if __name__ == "__main__":
    start_server()