import os
import unittest
from unittest.mock import patch

from rosseti_parser.config import get_mqtt_settings, get_settings
from rosseti_parser.startup import prepare_startup, validate_startup


class TestStartup(unittest.TestCase):
    def setUp(self):
        get_settings.cache_clear()
        get_mqtt_settings.cache_clear()

    def tearDown(self):
        get_settings.cache_clear()
        get_mqtt_settings.cache_clear()

    def test_validate_once_mode(self):
        env = {
            "LOGIN": "user@example.com",
            "PASSWORD": "secret",
            "METER_UUID": "00000000-0000-0000-0000-000000000000",
        }
        with patch.dict(os.environ, env, clear=True):
            summary = validate_startup(daemon=False)

        self.assertEqual(summary.mode, "once")
        self.assertFalse(summary.mqtt_enabled)
        self.assertIsNone(summary.schedule)

    def test_validate_daemon_mode(self):
        env = {
            "LOGIN": "user@example.com",
            "PASSWORD": "secret",
            "METER_UUID": "00000000-0000-0000-0000-000000000000",
            "SCHEDULE": "08:30,23:30",
            "TZ": "Europe/Moscow",
            "MQTT_HOST": "192.168.1.1",
            "MQTT_PORT": "1883",
            "MQTT_TOPIC": "rosseti/meter",
        }
        with patch.dict(os.environ, env, clear=True):
            summary = validate_startup(daemon=True)

        self.assertEqual(summary.mode, "daemon")
        self.assertTrue(summary.mqtt_enabled)
        self.assertEqual(summary.schedule, ("08:30", "23:30"))
        self.assertEqual(summary.timezone, "Europe/Moscow")

    def test_validate_missing_login(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                validate_startup(daemon=False)

    def test_validate_invalid_mqtt_port(self):
        env = {
            "LOGIN": "user@example.com",
            "PASSWORD": "secret",
            "METER_UUID": "00000000-0000-0000-0000-000000000000",
            "MQTT_HOST": "192.168.1.1",
            "MQTT_PORT": "bad",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                validate_startup(daemon=False)

    @patch("rosseti_parser.startup.log_startup")
    def test_prepare_startup(self, mock_log):
        env = {
            "LOGIN": "user@example.com",
            "PASSWORD": "secret",
            "METER_UUID": "00000000-0000-0000-0000-000000000000",
        }
        with patch.dict(os.environ, env, clear=True):
            summary = prepare_startup(daemon=False)

        self.assertEqual(summary.mode, "once")
        mock_log.assert_called_once_with(summary)


if __name__ == "__main__":
    unittest.main()
