import unittest
from app.categories import get_category_handler

class TestCategories(unittest.TestCase):
    def test_dentist_taboos(self):
        handler = get_category_handler("dentists")
        violations = handler.validate_voice("We offer 100% safe guaranteed cure")
        self.assertTrue(len(violations) > 0)

    def test_salons_formatting(self):
        handler = get_category_handler("salons")
        res = handler.format_offer_copy("Haircut", "99")
        self.assertEqual(res, "Haircut @ ₹99")

if __name__ == "__main__":
    unittest.main()
