"""
Unit tests for the client module.

This module contains tests for the Canvas API client initialization,
verifying proper handling of arguments and environment variables.
"""

import unittest
from unittest.mock import patch
import os
from canvas_tools.client import get_client

class TestClient(unittest.TestCase):
    """Test cases for the get_client function."""

    def test_get_client_with_args(self):
        """Test initializing client with explicit arguments."""

        with patch('canvas_tools.client.Canvas') as MockCanvas:
            client = get_client('http://test.url', 'test_key')
            MockCanvas.assert_called_once_with('http://test.url', 'test_key')
            self.assertIsNotNone(client)

    @patch.dict(os.environ, {'CANVAS_API_URL': 'http://env.url', 'CANVAS_API_KEY': 'env_key'})
    def test_get_client_with_env(self):
        """Test initializing client with environment variables."""

        with patch('canvas_tools.client.Canvas') as MockCanvas:
            client = get_client()
            MockCanvas.assert_called_once_with('http://env.url', 'env_key')

    @patch('canvas_tools.client.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_client_missing_config(self, mock_load_dotenv):
        """Test that ValueError is raised when configuration is missing."""

        with self.assertRaises(ValueError):
            get_client()

if __name__ == '__main__':
    unittest.main()
