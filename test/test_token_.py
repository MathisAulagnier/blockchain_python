import unittest

from src.token_ import Token
from datetime import datetime
import uuid
import hashlib
import json

class TestToken(unittest.TestCase):
    def test_token_initialization(self):
        """Test the initialization of a Token object"""
        token = Token()
        self.assertIsInstance(token.identifier, str, "Identifier should be a string")
        self.assertFalse(token.staking, "Staking should be False by default")
        self.assertIsInstance(token.created_at, float, "Created_at should be a float")
        self.assertIsInstance(token.hash, str, "Hash should be a string")

    def test_calculate_hash(self):
        """Test the hash calculation of a Token object"""
        token = Token()
        token_string = json.dumps({
            "identifier": token.identifier,
            "created_at": token.created_at
        }, sort_keys=True).encode()
        expected_hash = hashlib.sha256(token_string).hexdigest()
        self.assertEqual(token.hash, expected_hash, "Hash should match the expected value")

    def test_toggle_staking(self):
        """Test toggling the staking attribute"""
        token = Token()
        initial_hash = token.hash
        token.toggle_staking()
        self.assertTrue(token.staking)
        self.assertEqual(token.hash, initial_hash, "PROBLEME ICI")
        token.toggle_staking()
        self.assertFalse(token.staking)

    def test_to_dict(self):
        """Test the conversion of a Token object to a dictionary"""
        token = Token()
        token_dict = token.to_dict()
        self.assertEqual(token_dict["identifier"], token.identifier)
        self.assertEqual(token_dict["staking"], token.staking)
        self.assertEqual(token_dict["created_at"], token.created_at)
        self.assertEqual(token_dict["hash"], token.hash)

    def test_repr(self):
        """Test the string representation of a Token object"""
        token = Token()
        repr_string = repr(token)
        self.assertIn(f"Token(id={token.identifier[:8]}...", repr_string)
        self.assertIn(f"staking={token.staking})", repr_string)
