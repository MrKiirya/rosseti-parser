import unittest
from datetime import date

from rosseti_parser.output.payload import build_payload
from rosseti_parser.parsing.parser import extract_table_html, parse_latest_reading

DUAL_TARIFF_RESPONSE = (
    '$("#history_table_body").html("  <tr class=\\"odd\\">\\n'
    '    <td>05.07.2026<\\/td>\\n'
    '    <td>\\n'
    '        <p>День (7:00-23:00) Т1<\\/p>\\n'
    '        <p>Ночь (23:00-7:00) Т2<\\/p>\\n'
    '    <\\/td>\\n'
    '    <td>\\n'
    '        <p>501<br><\\/p>\\n'
    '        <p>187<br><\\/p>\\n'
    '    <\\/td>\\n'
    '    <td>«Россети Московский регион»<\\/td>\\n'
    '    <td>\\n    <\\/td>\\n'
    '  <\\/tr>\\n");'
)

SINGLE_TARIFF_RESPONSE = (
    '$("#history_table_body").html("  <tr class=\\"odd\\">\\n'
    '    <td>16.02.2026<\\/td>\\n'
    '    <td>\\n'
    '        <p>Однотарифный учёт электроэнергии<\\/p>\\n'
    '    <\\/td>\\n'
    '    <td>\\n'
    '        <p>230<br><\\/p>\\n'
    '    <\\/td>\\n'
    '    <td>«Россети Московский регион»<\\/td>\\n'
    '    <td>\\n    <\\/td>\\n'
    '  <\\/tr>\\n");'
)


class TestParser(unittest.TestCase):
    def test_extract_table_html(self):
        html = extract_table_html(DUAL_TARIFF_RESPONSE)
        self.assertIn("05.07.2026", html)
        self.assertIn("501", html)

    def test_parse_dual_tariff_reading(self):
        reading = parse_latest_reading(DUAL_TARIFF_RESPONSE)
        self.assertEqual(reading.t1, 501)
        self.assertEqual(reading.t2, 187)
        self.assertEqual(reading.reading_date, date(2026, 7, 5))
        self.assertEqual(reading.transmitted_by, "«Россети Московский регион»")

    def test_parse_single_tariff_reading(self):
        reading = parse_latest_reading(SINGLE_TARIFF_RESPONSE)
        self.assertEqual(reading.t1, 230)
        self.assertIsNone(reading.t2)
        self.assertEqual(reading.reading_date, date(2026, 2, 16))
        self.assertEqual(reading.transmitted_by, "«Россети Московский регион»")

    def test_build_payload_dual_tariff(self):
        reading = parse_latest_reading(DUAL_TARIFF_RESPONSE)
        payload = build_payload(reading)
        self.assertEqual(payload["t1"], 501)
        self.assertEqual(payload["t2"], 187)
        self.assertEqual(payload["reading_date"], "2026-07-05")
        self.assertEqual(payload["transmitted_by"], "«Россети Московский регион»")
        self.assertEqual(payload["source"], "rosseti")
        self.assertIn("T", payload["received_at"])

    def test_build_payload_single_tariff(self):
        reading = parse_latest_reading(SINGLE_TARIFF_RESPONSE)
        payload = build_payload(reading)
        self.assertEqual(payload["t1"], 230)
        self.assertIsNone(payload["t2"])
        self.assertEqual(payload["transmitted_by"], "«Россети Московский регион»")


if __name__ == "__main__":
    unittest.main()
