import argparse
import json
import logging
import os
import sys
from pathlib import Path

from rosseti_parser.config import load_env_file
from rosseti_parser.log_config import setup_logging
from rosseti_parser.runner import run_once
from rosseti_parser.scheduler import run_scheduler
from rosseti_parser.startup import prepare_startup

logger = logging.getLogger(__name__)


def _is_daemon_mode(cli_daemon: bool) -> bool:
    return cli_daemon or os.environ.get("MODE") == "daemon"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file with LOGIN, PASSWORD, METER_UUID",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run scheduler daemon (or MODE=daemon)",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    env_file = args.env_file or Path(".env")
    if env_file.is_file():
        logger.debug("Loading env from %s", env_file)
        load_env_file(env_file)

    daemon = _is_daemon_mode(args.daemon)
    prepare_startup(daemon)

    if daemon:
        run_scheduler()
        return

    payload = run_once()
    json_output = json.dumps(payload, ensure_ascii=False)

    sys.stdout.write(json_output)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
