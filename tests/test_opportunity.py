import unittest
from app.engine.opportunity_engine import OpportunityEngine

class TestOpportunityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OpportunityEngine()

    def test_recent_search_detection(self):
        cat = {"slug": "dentists"}
        merch = {
            "merchant_id": "m_001",
            "category_slug": "dentists",
            "identity": {"name": "Dr Meera"},
            "recent_searches": [{"query": "Dental Check Up", "count": 190}]
        }
        trig = {"id": "trg_001", "kind": "recent_search", "urgency": 4, "payload": {"query": "Dental Check Up"}}

        opp = self.engine.select_dominant_opportunity(cat, merch, trig)
        self.assertIsNotNone(opp)
        self.assertIn("recent_search", opp.signal_type)

if __name__ == "__main__":
    unittest.main()
