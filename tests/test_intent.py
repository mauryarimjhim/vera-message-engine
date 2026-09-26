import unittest
from app.engine.intent_engine import IntentEngine

class TestIntentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = IntentEngine()

    def test_intent_classification(self):
        self.assertEqual(self.engine.classify_intent("yes do it"), "YES")
        self.assertEqual(self.engine.classify_intent("no thanks, not interested"), "NO")
        self.assertEqual(self.engine.classify_intent("maybe tomorrow"), "LATER")
        self.assertEqual(self.engine.classify_intent("how much does it cost?"), "QUESTION")
        self.assertEqual(self.engine.classify_intent("Thank you for contacting us! Our team will respond shortly."), "AUTO_REPLY")
        self.assertEqual(self.engine.classify_intent("Stop messaging me. This is useless spam."), "HOSTILE")

if __name__ == "__main__":
    unittest.main()
