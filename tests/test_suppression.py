import unittest
from app.engine.suppression_engine import SuppressionEngine
from app.models.signal import OpportunitySignal
from app.storage.state_store import state_store

class TestSuppressionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SuppressionEngine()
        state_store.clear()

    def test_suppression(self):
        sig = OpportunitySignal(signal_type="recent_search", identifier="dental_check_up")
        
        # First check -> should not suppress
        supp, key, _ = self.engine.should_suppress("m_001", "dentists", sig)
        self.assertFalse(supp)
        
        # Mark key suppressed
        state_store.suppress_key(key)
        
        # Second check -> should suppress
        supp2, _, _ = self.engine.should_suppress("m_001", "dentists", sig)
        self.assertTrue(supp2)

if __name__ == "__main__":
    unittest.main()
