# common_socket_utils.py (Nouveau fichier pour les fonctions utilitaires)
import socket
import json
import struct # Pour packer/unpacker la longueur

HEADER_LENGTH = 4 # 4 bytes pour la longueur du message

def send_message(sock, message_dict):
    """Encode un dict en JSON, préfixe par sa longueur et l'envoie via le socket."""
    try:
        json_message = json.dumps(message_dict).encode('utf-8')
        message_length = len(json_message)
        # Pack la longueur en 4 bytes, big-endian ('>I')
        header = struct.pack('>I', message_length)
        sock.sendall(header + json_message)
        # print(f"[DEBUG send] Header: {header.hex()}, Length: {message_length}, Data: {message_dict}") # Debug
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi du message: {e}")
        # Tenter de fermer proprement le socket en cas d'erreur d'envoi majeure
        try:
            sock.close()
        except:
            pass
        return False

def receive_message(sock):
    """Reçoit un message préfixé par sa longueur depuis le socket et le décode de JSON."""
    try:
        # Lire le header (longueur du message)
        header_data = sock.recv(HEADER_LENGTH)
        if not header_data or len(header_data) < HEADER_LENGTH:
            # Connexion probablement fermée ou interrompue
            print("[DEBUG recv] Header incomplet ou connexion fermée.")
            return None
        # Unpack la longueur
        message_length = struct.unpack('>I', header_data)[0]
        # print(f"[DEBUG recv] Header: {header_data.hex()}, Expected Length: {message_length}") # Debug

        # Lire le message complet basé sur la longueur annoncée
        chunks = []
        bytes_received = 0
        while bytes_received < message_length:
            # Lire par morceaux pour éviter de bloquer sur de très gros messages
            chunk = sock.recv(min(message_length - bytes_received, 4096))
            if not chunk:
                # Connexion fermée prématurément
                print("[DEBUG recv] Connexion fermée pendant la lecture du message.")
                return None
            chunks.append(chunk)
            bytes_received += len(chunk)

        json_message = b''.join(chunks).decode('utf-8')
        # print(f"[DEBUG recv] Received JSON: {json_message}") # Debug
        message_dict = json.loads(json_message)
        return message_dict

    except struct.error as e:
        print(f"Erreur lors du unpacking du header: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur lors du décodage JSON: {e}")
        print(f"  -> Données reçues (partiel?): {b''.join(chunks).decode('utf-8', errors='ignore')}")
        return None
    except ConnectionResetError:
        print("Erreur: Connexion réinitialisée par le pair.")
        return None
    except socket.timeout:
        print("Erreur: Timeout lors de la réception.")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors de la réception du message: {e}")
        return None