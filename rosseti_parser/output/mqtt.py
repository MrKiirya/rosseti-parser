import json
import logging

import paho.mqtt.publish as publish

from rosseti_parser.config import get_mqtt_settings

logger = logging.getLogger(__name__)

STATUS_ONLINE = "online"


def _auth(settings) -> dict | None:
    if not settings.username:
        return None
    return {
        "username": settings.username,
        "password": settings.password or "",
    }


def _publish(topic: str, payload: str, settings, *, retain: bool) -> None:
    publish.single(
        topic,
        payload=payload,
        hostname=settings.host,
        port=settings.port,
        auth=_auth(settings),
        retain=retain,
    )


def publish_status(status: str = STATUS_ONLINE) -> bool:
    settings = get_mqtt_settings()
    if settings is None:
        return False

    _publish(settings.status_topic, status, settings, retain=True)
    logger.debug(
        "Published status %s to mqtt://%s:%s/%s",
        status,
        settings.host,
        settings.port,
        settings.status_topic,
    )
    return True


def publish_payload(payload: dict) -> bool:
    settings = get_mqtt_settings()
    if settings is None:
        logger.debug("MQTT not configured, skipping publish")
        return False

    _publish(
        settings.topic,
        json.dumps(payload, ensure_ascii=False),
        settings,
        retain=settings.retain,
    )
    _publish(settings.status_topic, STATUS_ONLINE, settings, retain=True)
    logger.debug(
        "Published to mqtt://%s:%s/%s",
        settings.host,
        settings.port,
        settings.topic,
    )
    return True
