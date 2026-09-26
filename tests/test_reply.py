import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.state_store import state_store

class TestReplyEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        state_store.clear()

    def test_reply_yes(self):
        res = self.client.post("/v1/reply", json={
            "conversation_id": "conv_001",
            "merchant_id": "m_001",
            "from_role": "merchant",
            "message": "Yes, send me the abstract",
            "received_at": "2026-04-26T10:00:00Z",
            "turn_number": 2
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["action"], "send")

    def test_reply_auto_reply_exit(self):
        auto_msg = "Thank you for contacting us! Our team will respond shortly."
        for i in range(1, 4):
            res = self.client.post("/v1/reply", json={
                "conversation_id": "conv_auto",
                "merchant_id": "m_001",
                "from_role": "merchant",
                "message": auto_msg,
                "received_at": "2026-04-26T10:00:00Z",
                "turn_number": i
            })
        data = res.json()
        self.assertEqual(data["action"], "end")

if __name__ == "__main__":
    unittest.main()
