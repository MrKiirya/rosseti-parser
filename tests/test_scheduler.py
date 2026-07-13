import unittest

from rosseti_parser.scheduler import parse_schedule


class TestScheduler(unittest.TestCase):
    def test_parse_schedule(self):
        self.assertEqual(parse_schedule("08:30,23:30"), [(8, 30), (23, 30)])

    def test_parse_schedule_with_spaces(self):
        self.assertEqual(parse_schedule(" 08:30 , 23:30 "), [(8, 30), (23, 30)])

    def test_parse_schedule_invalid(self):
        with self.assertRaises(ValueError):
            parse_schedule("invalid")

    def test_parse_schedule_empty(self):
        with self.assertRaises(ValueError):
            parse_schedule("")


if __name__ == "__main__":
    unittest.main()
