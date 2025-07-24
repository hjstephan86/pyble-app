# main_test.py - Integration tests for main.py (FastAPI application)

import unittest
from fastapi.testclient import TestClient

# Import the main app and database components
from main import app
from models import BibleVerse # For clearing data

# Create a test client
client = TestClient(app)

class TestMainApp(unittest.TestCase):

    def test_health_check(self):
        """Test the /health endpoint."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "UP", "version": "1.0.0", "application": "Bible App"})

    def test_app_info(self):
        """Test the /info endpoint."""
        response = client.get("/info")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self.assertEqual(info["name"], "Bible App")
        self.assertEqual(info["version"], "1.0.0")
        self.assertIn("api_docs", info["endpoints"])

    def test_swagger_docs(self):
        """Test the /swagger (docs_url) endpoint."""
        response = client.get("/swagger")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Swagger UI", response.content)

    def test_redoc_docs(self):
        """Test the /redoc (redoc_url) endpoint."""
        response = client.get("/redoc")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ReDoc", response.content)

if __name__ == '__main__':
    unittest.main()
