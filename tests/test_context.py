import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.context_store import context_store

class TestContextEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        context_store.clear()

    def test_push_context_success(self):
        payload = {
            "scope": "category",
            "context_id": "dentists",
            "version": 1,
            "payload": {"slug": "dentists"}
        }
        res = self.client.post("/v1/context", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["accepted"])

    def test_push_context_stale_version(self):
        payload = {
            "scope": "merchant",
            "context_id": "m_001",
            "version": 2,
            "payload": {"merchant_id": "m_001"}
        }
        self.client.post("/v1/context", json=payload)

        # Same version push
        res = self.client.post("/v1/context", json=payload)
        self.assertEqual(res.status_code, 409)
        self.assertFalse(res.json()["accepted"])

    def test_invalid_scope(self):
        payload = {
            "scope": "invalid_scope",
            "context_id": "x",
            "version": 1,
            "payload": {}
        }
        res = self.client.post("/v1/context", json=payload)
        self.assertEqual(res.status_code, 400)

if __name__ == "__main__":
    unittest.main()
