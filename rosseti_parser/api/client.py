import logging
from datetime import date

import requests
from bs4 import BeautifulSoup

from rosseti_parser import config
from rosseti_parser.api.dates import format_date, month_ago

logger = logging.getLogger(__name__)

BASE_URL = "https://lk.rossetimr.ru"
SIGN_IN_URL = f"{BASE_URL}/users/sign_in"
READOUTS_NEW_URL = f"{BASE_URL}/electricity_meter_readouts/new"
HISTORY_URL = f"{BASE_URL}/electricity_meter_readouts/show_history"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)


def _page_summary(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    parts = []
    if soup.title and soup.title.string:
        parts.append(soup.title.string.strip())
    for tag in ("h1", "h2"):
        element = soup.find(tag)
        if element:
            parts.append(element.get_text(strip=True))
    return " | ".join(parts) if parts else f"{len(html)} bytes"


def _extract_csrf_token(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find("meta", {"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    token_input = soup.find("input", {"name": "authenticity_token"})
    if token_input and token_input.get("value"):
        return token_input["value"]
    return None


def get_history() -> str:
    settings = config.get_settings()
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    logger.debug("Opening login page: %s", SIGN_IN_URL)
    login_page = session.get(SIGN_IN_URL)
    logger.debug("Login page: status=%s", login_page.status_code)
    login_page.raise_for_status()

    token = _extract_csrf_token(login_page.text)
    if not token:
        logger.error("CSRF token not found on login page")
        raise RuntimeError("CSRF token not found on login page")
    logger.debug("CSRF token received")

    logger.debug("Logging in as %s", settings.login)
    login_response = session.post(
        SIGN_IN_URL,
        data={
            "utf8": "✓",
            "authenticity_token": token,
            "user[email]": settings.login,
            "user[password]": settings.password,
        },
        headers={"Referer": SIGN_IN_URL},
    )
    logger.debug(
        "Login response: status=%s url=%s",
        login_response.status_code,
        login_response.url,
    )

    if "sign_in" in login_response.url:
        summary = _page_summary(login_response.text)
        logger.error("Login failed: %s", summary)
        raise RuntimeError(f"Login failed: {summary}")

    logger.debug("Opening readouts page: %s", READOUTS_NEW_URL)
    readouts_page = session.get(READOUTS_NEW_URL)
    logger.debug("Readouts page: status=%s", readouts_page.status_code)
    readouts_page.raise_for_status()

    csrf_token = _extract_csrf_token(readouts_page.text)
    if not csrf_token:
        logger.error("CSRF token not found on readouts page")
        raise RuntimeError("CSRF token not found on readouts page")
    logger.debug("CSRF token for XHR received")

    today = date.today()
    date_start = format_date(month_ago(today))
    date_end = format_date(today)
    params = {
        "meter_uuid": settings.meter_uuid,
        "date_start": date_start,
        "date_end": date_end,
    }

    logger.debug(
        "Fetching history: meter=%s period=%s..%s",
        settings.meter_uuid,
        date_start,
        date_end,
    )
    response = session.get(
        HISTORY_URL,
        params=params,
        headers={
            "Accept": "*/*",
            "Referer": READOUTS_NEW_URL,
            "X-CSRF-Token": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    logger.debug(
        "History response: status=%s bytes=%s",
        response.status_code,
        len(response.text),
    )

    if response.status_code >= 400:
        summary = _page_summary(response.text)
        logger.error("History request failed: %s", summary)
        raise RuntimeError(
            f"History request failed (HTTP {response.status_code}): {summary}"
        )

    return response.text
