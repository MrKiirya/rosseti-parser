import json
import logging

import paho.mqtt.publish as publish

from rosseti_parser.config import get_mqtt_settings

logger = logging.getLogger(__name__)


def publish_payload(payload: dict) -> bool:
    settings = get_mqtt_settings()
    if settings is None:
        logger.debug("MQTT not configured, skipping publish")
        return False

    auth = None
    if settings.username:
        auth = {
            "username": settings.username,
            "password": settings.password or "",
        }

    publish.single(
        settings.topic,
        payload=json.dumps(payload, ensure_ascii=False),
        hostname=settings.host,
        port=settings.port,
        auth=auth,
        retain=settings.retain,
    )
    logger.debug(
        "Published to mqtt://%s:%s/%s",
        settings.host,
        settings.port,
        settings.topic,
    )
    return True
