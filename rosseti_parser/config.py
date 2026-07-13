import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def load_env_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Env file not found: {path}")
    load_dotenv(path)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    login: str
    password: str
    meter_uuid: str


@dataclass(frozen=True)
class MqttSettings:
    host: str
    port: int
    topic: str
    status_topic: str
    username: str | None
    password: str | None
    retain: bool


@lru_cache
def get_settings() -> Settings:
    return Settings(
        login=_require_env("LOGIN"),
        password=_require_env("PASSWORD"),
        meter_uuid=_require_env("METER_UUID"),
    )


@lru_cache
def get_mqtt_settings() -> MqttSettings | None:
    host = os.environ.get("MQTT_HOST")
    if not host:
        return None

    port_raw = os.environ.get("MQTT_PORT", "1883")
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError("MQTT_PORT must be an integer") from exc

    topic = os.environ.get("MQTT_TOPIC", "rosseti/meter")
    if not topic.strip():
        raise RuntimeError("MQTT_TOPIC must not be empty")
    topic = topic.strip()
    status_topic = os.environ.get("MQTT_STATUS_TOPIC", f"{topic}/status").strip()
    if not status_topic:
        raise RuntimeError("MQTT_STATUS_TOPIC must not be empty")

    return MqttSettings(
        host=host.strip(),
        port=port,
        topic=topic,
        status_topic=status_topic,
        username=os.environ.get("MQTT_USER") or None,
        password=os.environ.get("MQTT_PASSWORD") or None,
        retain=_env_bool("MQTT_RETAIN", True),
    )
