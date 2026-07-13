import unittest
from datetime import date

from rosseti_parser.api.dates import format_date, month_ago


class TestDates(unittest.TestCase):
    def test_format_date(self):
        self.assertEqual(format_date(date(2026, 7, 7)), "07.07.2026")

    def test_month_ago(self):
        self.assertEqual(month_ago(date(2026, 7, 7)), date(2026, 6, 7))
        self.assertEqual(month_ago(date(2026, 1, 31)), date(2025, 12, 31))
        self.assertEqual(month_ago(date(2026, 3, 31)), date(2026, 2, 28))


if __name__ == "__main__":
    unittest.main()
