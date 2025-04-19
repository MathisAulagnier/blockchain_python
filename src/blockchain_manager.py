import time
from src.blockchain import Blockchain
from src.token_manager import TokenManager
from src.wallet_manager import WalletManager
from src.pbft import PBFT  
import random

class BlockchainManager(Blockchain):
    def __init__(self, initial_supply=100, origin_wallet="wallet_creator", transaction_threshold=2):
        super().__init__()
        self.token_manager = TokenManager(max_tokens=initial_supply)  # Gestionnaire de tokens
        self.wallet_manager = WalletManager() 
        self.validators = []             # Liste des validateurs
        self.manual_votes = {}           # Dictionnaire pour les votes manuels des validateurs
        self.stakes = {}                 # Dictionnaire associant validateur et montant staké
        self.pbft = PBFT(self.validators, self.stakes) 
        self.transaction_threshold = transaction_threshold  # Seuil d'automatisme de commit
        self.origin_wallet = origin_wallet
        

        # Création (ou récupération) du wallet d'origine
        try:
            self.wallet_manager.get_wallet(self.origin_wallet)
        except ValueError:
            self.wallet_manager.create_wallet(self.origin_wallet)
        # Création de l'offre initiale et commit immédiat des transactions de création si token n'est pas à 0
        if initial_supply > 0:
            self.create_initial_supply(count=initial_supply + 3 , origin_wallet=self.origin_wallet)
        
    def add_transaction(self, transaction):
        """
        Ajoute une transaction (ou une liste de transactions) à la file d'attente.
        et déclenche la validation dès que le seuil est atteint.
        """
        if isinstance(transaction, list):
            self.pending_transactions.extend(transaction)
        else:
            self.pending_transactions.append(transaction)
        
        # Vérifier si le nombre de transactions atteint le seuil pour commiter
        if len(self.pending_transactions) >= self.transaction_threshold:
            self.commit_pending_transactions()
            
    def commit_pending_transactions(self):
        """
        Exécute le processus de consensus PBFT pour valider et ajouter le bloc contenant les transactions en attente.
        Avant de lancer le consensus, affiche pour chaque transaction son type (création, transfert, stake, unstake, etc.).
        """
        if not self.pending_transactions:
            print("Aucune transaction à commiter.")
            return

        print("\n⛓️ Lancement du consensus PBFT...")

        # Création du bloc candidat en utilisant la méthode dédiée de la classe Blockchain
        candidate_block = self.create_candidate_block(self.pending_transactions.copy())

        # Affichage des transactions du bloc candidat avec leur type
        print("Transactions dans le bloc candidat :")
        for tx in candidate_block.transactions:
            # On suppose que chaque transaction est un dictionnaire avec une clé "action"
            action = tx.get("action", "inconnue")
            if action == "token_creation":
                print("  - Création de tokens pour wallet:", tx.get("owner"))
            elif action == "transfer":
                print("  - Transfert de token {} de {} vers {}".format(tx.get("token_id"), tx.get("from"), tx.get("to")))
            elif action == "stake":
                print("  - Staking du token {} pour {}".format(tx.get("token_id"), tx.get("address")))
            elif action == "unstake":
                print("  - Unstaking du token {} pour {}".format(tx.get("token_id"), tx.get("address")))
            else:
                print("  - Transaction de type {}: {}".format(action, tx))

        # Sélection du leader grâce au mécanisme PoS
        leader = self.choose_validator()
        print("🧑‍⚖️ Validateur choisi (leader) :", leader)

        # Phase de pre-prepare : appel de la méthode du protocole PBFT
        self.pbft.pre_prepare(candidate_block, leader)

        # Phase de prepare : chaque validateur vote sur le bloc candidat
        for validator in self.validators:
            vote = self.decide_vote(validator, candidate_block)
            print(f"🗳️ {validator} vote {'✅' if vote else '❌'}")
            self.pbft.prepare(candidate_block, validator, vote)

        # Phase de commit : obtenir le résultat du consensus
        success, message = self.pbft.commit(candidate_block)
        print(message)

        if success:
            signature = self.pbft.get_consensus_signature(candidate_block)
            self.add_block(leader, signature)
            print(f"✅ Bloc {candidate_block.index} ajouté !\n")
            #Print hash 
            print(f"Hash du bloc {candidate_block.index} : {candidate_block.hash}\n")

        else:
            print("❌ Consensus échoué, annulation des TX...\n")
            for undo in reversed(self.pending_rollbacks):
                try:
                    undo()
                except Exception as e:
                    print(f"[ROLLBACK ERREUR] {e}")
            self.pending_transactions.clear()
            self.pending_rollbacks.clear()


    def decide_vote(self, validator, block):
        """
        Retourne le vote défini manuellement pour le validateur.
        Si aucun vote n'est défini, retourne True par défaut.
        """
        return self.manual_votes.get(validator, True)

    
    def create_initial_supply(self, count=248, origin_wallet="wallet_creator"):
        """
        Crée l'offre initiale de tokens et les attribue au wallet d'origine.
        La transaction de création est ajoutée aux transactions en attente
        puis committée immédiatement dans un bloc unique.
        
        Ce bloc unique inclut :
        - La création initiale des tokens,
        - Le transfert des tokens vers les wallets de base (wallet_Lina, wallet_Mathis, wallet_JJ),
        - Le staking (1 token) de chacun de ces wallets pour qu'ils deviennent validateurs.
        """
        # Pour s'assurer que toutes les transactions sont regroupées dans un seul bloc,
        # on désactive temporairement le déclenchement automatique du commit.
        original_threshold = self.transaction_threshold
        self.transaction_threshold = 10**9  # Valeur très élevée pour éviter les commits intermédiaires

        # --- Création des tokens initiaux ---
        tokens = self.token_manager.create_initial_tokens(count)
        try:
            owner_wallet = self.wallet_manager.get_wallet(origin_wallet)
        except ValueError:
            owner_wallet = self.wallet_manager.create_wallet(origin_wallet)
        for token in tokens:
            owner_wallet.deposit_token(token.identifier, stake=False)
        token_data = [token.to_dict() for token in tokens]
        # Ajout de la transaction de création des tokens
        self.pending_transactions.append({
            "action": "token_creation",
            "owner": origin_wallet,
            "tokens": token_data
        })
        
        # --- Création et staking des wallets initiaux ---
        # On crée et crédite trois wallets de base, puis on stake 1 token pour chacun.
        self.create_and_stake_initial_wallet("wallet_Lina", initial_credit=15, stake_count=1)
        self.create_and_stake_initial_wallet("wallet_Mathis", initial_credit=15, stake_count=1)
        self.create_and_stake_initial_wallet("wallet_JJ", initial_credit=15, stake_count=1)
        
        self.add_block(origin_wallet, "INITIAL_SUPPLY")
        # On vide la file des transactions en attente
        self.pending_transactions = []
        self.pending_rollbacks = []
        
        # Restauration du seuil de commit d'origine
        self.transaction_threshold = original_threshold
        
        return tokens

    def transfer_token(self, token_id, from_address, to_address):
        """
        Transfère un token d'un wallet à un autre et ajoute la transaction en file.
        Le transfert n'est pas immédiatement validé par la création d'un bloc.
        """
        from_w = self.wallet_manager.get_wallet(from_address)
        to_w   = self.wallet_manager.get_wallet(to_address)
        if token_id not in from_w.available_tokens:
            raise ValueError("Token non dispo")
        from_w.withdraw_token(token_id)
        to_w.deposit_token(token_id, stake=False)
        # rollback
        def undo():
            w_to = self.wallet_manager.get_wallet(to_address)
            w_from = self.wallet_manager.get_wallet(from_address)
            w_to.withdraw_token(token_id)
            w_from.deposit_token(token_id, stake=False)
        self.pending_rollbacks.append(undo)
        tx = {
            "action": "transfer",
            "token_id": token_id,
            "from": from_address,
            "to": to_address,
            "timestamp": time.time()
        }
        self.add_transaction(tx)
        return tx

    def stake_token(self, token_id, address):
        """
        Déplace un token du solde disponible vers le solde staké dans le wallet spécifié,
        et ajoute la transaction en file.
        """
        wallet = self.wallet_manager.get_wallet(address)
        if token_id not in wallet.available_tokens:
            raise ValueError(f"Token {token_id} n'est pas disponible dans le wallet {address} pour être staké")
        wallet.stake_token(token_id)
        def undo():
            self.wallet_manager.get_wallet(address).unstake_token(token_id)
        self.pending_rollbacks.append(undo)
        transaction = {
            "action": "stake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_transaction(transaction)
        self.register_validator(address, stake=1)
        return transaction

    def unstake_token(self, token_id, address):
        """
        Déplace un token du solde staké vers le solde disponible du wallet spécifié,
        et ajoute la transaction en file.
        """
        wallet = self.wallet_manager.get_wallet(address)
        if token_id not in wallet.staked_tokens:
            raise ValueError(f"Token {token_id} n'est pas en staking dans le wallet {address}")
        wallet.unstake_token(token_id)
        def undo():
            self.wallet_manager.get_wallet(address).stake_token(token_id)
        self.pending_rollbacks.append(undo)
        transaction = {
            "action": "unstake",
            "token_id": token_id,
            "address": address,
            "timestamp": time.time()
        }
        self.add_transaction(transaction)
        return transaction

    def get_token_history(self, token_id):
        """Retourne l'historique des transactions pour un token spécifique."""
        token_transactions = []
        for block in self.chain:
            for transaction in block.transactions:
                # Si la transaction individuelle concerne ce token
                if isinstance(transaction, dict) and transaction.get("token_id") == token_id:
                    t = transaction.copy()
                    t["block_hash"] = block.hash
                    t["block_index"] = block.index
                    token_transactions.append(t)
                # Pour une transaction groupée de création
                elif (isinstance(transaction, dict) and 
                      transaction.get("action") == "token_creation" and 
                      "tokens" in transaction):
                    for token_data in transaction["tokens"]:
                        if token_data.get("identifier") == token_id:
                            creation_info = {
                                "action": "creation",
                                "token_id": token_id,
                                "timestamp": block.timestamp,
                                "block_hash": block.hash,
                                "block_index": block.index
                            }
                            token_transactions.append(creation_info)
        return token_transactions

    def get_token_by_index(self, index):
        """Récupère un token par son index dans la liste des tokens."""
        all_tokens = self.token_manager.get_all_tokens()
        if 0 <= index < len(all_tokens):
            return all_tokens[index]
        return None

    def get_staking_stats(self):
        all_tokens = self.token_manager.get_all_tokens()
        total_tokens = len(all_tokens)
        total_staked = sum(len(wallet.staked_tokens) for wallet in self.wallet_manager.wallets.values())
        staking_percentage = (total_staked / total_tokens * 100) if total_tokens > 0 else 0
        total_value = self.token_manager.get_tokens_value()
        single_value = total_value / total_tokens if total_tokens > 0 else 0
        return {
            "total_tokens": total_tokens,
            "staking_tokens": total_staked,
            "staking_percentage": staking_percentage,
            "total_value": total_value,
            "staking_value": single_value * total_staked
        }

    def create_wallet_for_user(self, user_address, initial_credit=5):
        """
        Crée un nouveau wallet pour un utilisateur et le crédite automatiquement avec un nombre fixe de tokens
        provenant du wallet d'origine.
        """
        new_wallet = self.wallet_manager.create_wallet(user_address)
        origin = self.origin_wallet
        origin_wallet = self.wallet_manager.get_wallet(origin)
        available_tokens = list(origin_wallet.available_tokens)
        if len(available_tokens) < initial_credit:
            raise ValueError("Tokens insuffisants dans le wallet d'origine pour créditer le nouveau wallet")
        for token_id in available_tokens[:initial_credit]:
            self.transfer_token(token_id, origin, user_address)
        return new_wallet
    
    def create_initial_wallet(self, user_address, initial_credit=5):
        """
        Crée un nouveau wallet pour un utilisateur et le crédite automatiquement avec un nombre fixe de tokens
        provenant du wallet d'origine.
        Cette fonction est destinée à être utilisée lors de l'initialisation de la blockchain
        et ajoute les transferts dans pending_transactions sans déclencher de commit.
        """
        new_wallet = self.wallet_manager.create_wallet(user_address)
        origin = self.origin_wallet
        origin_wallet = self.wallet_manager.get_wallet(origin)
        available_tokens = list(origin_wallet.available_tokens)
        if len(available_tokens) < initial_credit:
            raise ValueError("Tokens insuffisants dans le wallet d'origine pour créditer " + user_address)
        for token_id in available_tokens[:initial_credit]:
            origin_wallet.withdraw_token(token_id)
            new_wallet.deposit_token(token_id, stake=False)
            transaction = {
                "action": "transfer",
                "token_id": token_id,
                "from": origin,
                "to": user_address,
                "timestamp": time.time()
            }
            self.pending_transactions.append(transaction)
        return new_wallet

    
    def create_and_stake_initial_wallet(self, user_address, initial_credit, stake_count=1):
        """
        Crée un nouveau wallet pour un utilisateur (via create_initial_wallet) et le crédite 
        avec un nombre fixe de tokens provenant du wallet d'origine. Ensuite, pour simuler
        que ce wallet devient validateur, il stake 'stake_count' tokens (c'est-à-dire retire
        le ou les tokens du solde disponible et les place dans le solde staké via stake_token).
        
        La transaction de transfert est ajoutée à pending_transactions et sera incluse dans le bloc initial.
        """
        # Crée le wallet et effectue les transferts directs (sans commit)
        wallet = self.create_initial_wallet(user_address, initial_credit)
        # Pour chaque token à staker (au nombre de stake_count), on effectue le staking
        for _ in range(stake_count):
            available = list(wallet.available_tokens)
            if not available:
                break
            token_id = available[0]  # On choisit le premier token disponible
            # Utilise la méthode stake_token qui ajoute une transaction "stake" et inscrit le validateur
            self.stake_token(token_id, user_address)
        return wallet


    def register_validator(self, validator, stake):
        """
        Enregistre un validateur et met à jour son stake.
        """
        if validator not in self.validators:
            self.validators.append(validator)
        self.stakes[validator] = self.stakes.get(validator, 0) + stake

    def choose_validator(self):
        """
        Sélectionne un validateur de manière pondérée en fonction du stake.
        Un nombre aléatoire est tiré pour choisir parmi les validateurs en proportion de leur stake.
        :return: L'identifiant du validateur sélectionné
        """
        total_stake = sum(self.stakes.values())
        pick = random.uniform(0, total_stake)
        current = 0
        for validator, stake in self.stakes.items():
            current += stake
            if current > pick:
                return validator
        return None   