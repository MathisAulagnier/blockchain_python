import unittest
from unittest.mock import patch
from src.token_ import Token
from src.token_manager import TokenManager


class TestTokenManager(unittest.TestCase):
    def setUp(self):
        self.token_manager = TokenManager(max_tokens=100)
        
    def test_create_token(self):
        token = self.token_manager.create_token()
        self.assertIsInstance(token, Token)
        self.assertIn(token.identifier, self.token_manager.tokens)
        self.assertEqual(len(self.token_manager.tokens), 1)
        
    def test_create_multiple_tokens(self):
        tokens = self.token_manager.create_initial_tokens(count=5)
        self.assertEqual(len(tokens), 5)
        self.assertEqual(len(self.token_manager.tokens), 5)
        
    def test_max_tokens_limit(self):
        self.token_manager.create_initial_tokens(count=100)
        self.assertEqual(len(self.token_manager.tokens), 100)
        
        # Essayer d'en créer un de plus doit lever une exception
        with self.assertRaises(ValueError):
            self.token_manager.create_token()
            
    def test_get_token(self):
        token = self.token_manager.create_token()
        retrieved_token = self.token_manager.get_token(token.identifier)
        self.assertEqual(token, retrieved_token)
        
        # Test avec un ID inexistant
        self.assertIsNone(self.token_manager.get_token("nonexistent_id"))
        
    def test_get_staking_tokens(self):
        # Créer quelques tokens
        tokens = self.token_manager.create_initial_tokens(count=10)
        
        # Aucun token en staking au début
        self.assertEqual(len(self.token_manager.get_staking_tokens()), 0)
        
        # Mettre quelques tokens en staking
        tokens[0].staking = True
        tokens[3].staking = True
        tokens[7].staking = True
        
        staking_tokens = self.token_manager.get_staking_tokens()
        self.assertEqual(len(staking_tokens), 3)
        self.assertIn(tokens[0], staking_tokens, "Token 0 should be in staking tokens")
        self.assertIn(tokens[3], staking_tokens)
        self.assertIn(tokens[7], staking_tokens)
    


