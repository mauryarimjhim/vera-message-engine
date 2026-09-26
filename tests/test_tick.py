import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.context_store import context_store
from app.storage.state_store import state_store

class TestTickEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        context_store.clear()
        state_store.clear()

        # Push base contexts
        self.client.post("/v1/context", json={
            "scope": "category", "context_id": "dentists", "version": 1,
            "payload": {"slug": "dentists"}
        })
        self.client.post("/v1/context", json={
            "scope": "merchant", "context_id": "m_001", "version": 1,
            "payload": {"merchant_id": "m_001", "category_slug": "dentists", "identity": {"name": "Dr Meera"}}
        })
        self.client.post("/v1/context", json={
            "scope": "trigger", "context_id": "trg_001", "version": 1,
            "payload": {
                "id": "trg_001", "scope": "merchant", "kind": "recent_search", "source": "external",
                "merchant_id": "m_001", "payload": {"query": "Dental Check Up", "count": 190}, "urgency": 3
            }
        })

    def test_tick_action(self):
        res = self.client.post("/v1/tick", json={"now": "2026-04-26T10:00:00Z", "available_triggers": ["trg_001"]})
        self.assertEqual(res.status_code, 200)
        actions = res.json()["actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["merchant_id"], "m_001")

if __name__ == "__main__":
    unittest.main()
