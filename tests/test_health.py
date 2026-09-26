import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestHealthEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_healthz(self):
        response = self.client.get("/v1/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("uptime_seconds", data)
        self.assertIn("contexts_loaded", data)

    def test_metadata(self):
        response = self.client.get("/v1/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("team_name", data)
        self.assertIn("version", data)

if __name__ == "__main__":
    unittest.main()
