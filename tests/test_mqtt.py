import json
import os
import unittest
from unittest.mock import patch

from rosseti_parser.config import get_mqtt_settings
from rosseti_parser.output.mqtt import publish_payload, publish_status


class TestMqtt(unittest.TestCase):
    def setUp(self):
        get_mqtt_settings.cache_clear()

    def tearDown(self):
        get_mqtt_settings.cache_clear()

    def test_get_mqtt_settings_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(get_mqtt_settings())

    def test_get_mqtt_settings(self):
        with patch.dict(
            os.environ,
            {
                "MQTT_HOST": "192.168.1.1",
                "MQTT_PORT": "1883",
                "MQTT_TOPIC": "rosseti/meter",
                "MQTT_USER": "user",
                "MQTT_PASSWORD": "pass",
                "MQTT_RETAIN": "true",
            },
            clear=True,
        ):
            settings = get_mqtt_settings()
            self.assertEqual(settings.host, "192.168.1.1")
            self.assertEqual(settings.port, 1883)
            self.assertEqual(settings.topic, "rosseti/meter")
            self.assertEqual(settings.status_topic, "rosseti/meter/status")
            self.assertEqual(settings.username, "user")
            self.assertEqual(settings.password, "pass")
            self.assertTrue(settings.retain)

    @patch("rosseti_parser.output.mqtt.publish.single")
    def test_publish_payload(self, mock_single):
        payload = {"t1": 501, "t2": 187}
        with patch.dict(os.environ, {"MQTT_HOST": "192.168.1.1"}, clear=True):
            published = publish_payload(payload)

        self.assertTrue(published)
        self.assertEqual(mock_single.call_count, 2)

        payload_call = mock_single.call_args_list[0]
        status_call = mock_single.call_args_list[1]
        self.assertEqual(payload_call.args[0], "rosseti/meter")
        self.assertEqual(json.loads(payload_call.kwargs["payload"]), payload)
        self.assertEqual(status_call.args[0], "rosseti/meter/status")
        self.assertEqual(status_call.kwargs["payload"], "online")
        self.assertTrue(status_call.kwargs["retain"])

    @patch("rosseti_parser.output.mqtt.publish.single")
    def test_publish_status(self, mock_single):
        with patch.dict(os.environ, {"MQTT_HOST": "192.168.1.1"}, clear=True):
            published = publish_status()

        self.assertTrue(published)
        mock_single.assert_called_once()
        self.assertEqual(mock_single.call_args.args[0], "rosseti/meter/status")
        self.assertEqual(mock_single.call_args.kwargs["payload"], "online")

    @patch("rosseti_parser.output.mqtt.publish.single")
    def test_publish_skipped_when_not_configured(self, mock_single):
        with patch.dict(os.environ, {}, clear=True):
            published = publish_payload({"t1": 1})

        self.assertFalse(published)
        mock_single.assert_not_called()


if __name__ == "__main__":
    unittest.main()
