import logging
import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from rosseti_parser.config import get_mqtt_settings, get_settings
from rosseti_parser.scheduler import DEFAULT_SCHEDULE, DEFAULT_TIMEZONE, parse_schedule

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StartupSummary:
    mode: str
    login: str
    meter_uuid: str
    mqtt_enabled: bool
    mqtt_host: str | None = None
    mqtt_port: int | None = None
    mqtt_topic: str | None = None
    mqtt_status_topic: str | None = None
    mqtt_user: str | None = None
    mqtt_retain: bool | None = None
    schedule: tuple[str, ...] | None = None
    timezone: str | None = None


def _validate_mqtt_settings() -> None:
    settings = get_mqtt_settings()
    if settings is None:
        return

    if not settings.host.strip():
        raise RuntimeError("MQTT_HOST must not be empty")

    if not 1 <= settings.port <= 65535:
        raise RuntimeError(f"Invalid MQTT_PORT: {settings.port}")

    if not settings.topic.strip():
        raise RuntimeError("MQTT_TOPIC must not be empty")


def validate_startup(daemon: bool) -> StartupSummary:
    rosseti = get_settings()
    _validate_mqtt_settings()
    mqtt = get_mqtt_settings()

    schedule_labels: tuple[str, ...] | None = None
    timezone: str | None = None
    if daemon:
        schedule = parse_schedule(os.environ.get("SCHEDULE", DEFAULT_SCHEDULE))
        timezone = os.environ.get("TZ", DEFAULT_TIMEZONE)
        ZoneInfo(timezone)
        schedule_labels = tuple(f"{hour:02d}:{minute:02d}" for hour, minute in schedule)

    return StartupSummary(
        mode="daemon" if daemon else "once",
        login=rosseti.login,
        meter_uuid=rosseti.meter_uuid,
        mqtt_enabled=mqtt is not None,
        mqtt_host=mqtt.host if mqtt else None,
        mqtt_port=mqtt.port if mqtt else None,
        mqtt_topic=mqtt.topic if mqtt else None,
        mqtt_status_topic=mqtt.status_topic if mqtt else None,
        mqtt_user=mqtt.username if mqtt else None,
        mqtt_retain=mqtt.retain if mqtt else None,
        schedule=schedule_labels,
        timezone=timezone,
    )


def log_startup(summary: StartupSummary) -> None:
    logger.info("Starting in %s mode", summary.mode)
    logger.info("Rosseti login=%s meter=%s", summary.login, summary.meter_uuid)

    if summary.mqtt_enabled:
        auth = f" user={summary.mqtt_user}" if summary.mqtt_user else ""
        logger.info(
            "MQTT enabled: %s:%s/%s status=%s retain=%s%s",
            summary.mqtt_host,
            summary.mqtt_port,
            summary.mqtt_topic,
            summary.mqtt_status_topic,
            summary.mqtt_retain,
            auth,
        )
    else:
        logger.info("MQTT disabled (MQTT_HOST not set)")

    if summary.mode == "daemon":
        logger.info(
            "Scheduler: times=%s timezone=%s",
            ",".join(summary.schedule or ()),
            summary.timezone,
        )


def prepare_startup(daemon: bool) -> StartupSummary:
    summary = validate_startup(daemon)
    log_startup(summary)
    return summary
