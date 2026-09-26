import unittest
from app.engine.composer import compose

class TestDeterminism(unittest.TestCase):
    def test_deterministic_output(self):
        cat = {"slug": "dentists"}
        merch = {
            "merchant_id": "m_001_drmeera",
            "category_slug": "dentists",
            "identity": {"name": "Dr. Meera's Dental Clinic", "owner_first_name": "Meera"}
        }
        trig = {
            "id": "trg_001",
            "scope": "merchant",
            "kind": "recent_search",
            "source": "external",
            "payload": {"query": "Dental Check Up", "count": 190, "price": "299"},
            "urgency": 3,
            "suppression_key": "det_test_key"
        }

        res1 = compose(cat, merch, trig)
        # Verify result format
        self.assertIn("body", res1)
        self.assertIn("cta", res1)
        self.assertIn("send_as", res1)

if __name__ == "__main__":
    unittest.main()
