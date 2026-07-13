import logging
import os
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from rosseti_parser.runner import run_once

logger = logging.getLogger(__name__)

DEFAULT_SCHEDULE = "08:30,23:30"
DEFAULT_TIMEZONE = "Europe/Moscow"


def parse_schedule(value: str) -> list[tuple[int, int]]:
    times: list[tuple[int, int]] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            hour_str, minute_str = part.split(":", 1)
            hour = int(hour_str)
            minute = int(minute_str)
        except ValueError as exc:
            raise ValueError(
                f"Invalid schedule entry '{part}', expected HH:MM"
            ) from exc
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(
                f"Invalid schedule entry '{part}', hour/minute out of range"
            )
        times.append((hour, minute))

    if not times:
        raise ValueError("Schedule is empty")
    return times


def _scheduled_job() -> None:
    try:
        payload = run_once()
        logger.debug("Scheduled run completed: %s", payload)
    except Exception:
        logger.exception("Scheduled run failed")


def run_scheduler() -> None:
    schedule = parse_schedule(os.environ.get("SCHEDULE", DEFAULT_SCHEDULE))
    timezone = ZoneInfo(os.environ.get("TZ", DEFAULT_TIMEZONE))

    scheduler = BlockingScheduler(timezone=timezone)
    for hour, minute in schedule:
        scheduler.add_job(
            _scheduled_job,
            CronTrigger(hour=hour, minute=minute, timezone=timezone),
        )

    logger.info("Scheduler started")
    scheduler.start()
