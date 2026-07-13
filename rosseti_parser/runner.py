import logging

from rosseti_parser.api.client import get_history
from rosseti_parser.output.mqtt import publish_payload
from rosseti_parser.output.payload import build_payload
from rosseti_parser.parsing.parser import parse_latest_reading

logger = logging.getLogger(__name__)


def run_once() -> dict:
    raw = get_history()
    payload = build_payload(parse_latest_reading(raw))
    mqtt_published = publish_payload(payload)

    logger.info(
        "Run completed: date=%s t1=%s t2=%s mqtt=%s",
        payload["reading_date"],
        payload["t1"],
        payload["t2"],
        "published" if mqtt_published else "skipped",
    )
    return payload
