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


