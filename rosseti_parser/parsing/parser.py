import json
import logging
import re
from datetime import date

from bs4 import BeautifulSoup

from rosseti_parser.parsing.models import MeterReading

logger = logging.getLogger(__name__)

HTML_PREFIX = '.html("'
HTML_SUFFIX = '");'
SINGLE_TARIFF_MARKER = "Однотарифный"


def extract_table_html(raw: str) -> str:
    start = raw.find(HTML_PREFIX)
    if start == -1:
        raise ValueError("History table not found in response")
    start += len(HTML_PREFIX)
    end = raw.rfind(HTML_SUFFIX)
    if end == -1 or end <= start:
        raise ValueError("History table not found in response")
    return json.loads(f'"{raw[start:end]}"')


def _parse_reading_date(value: str) -> date:
    day, month, year = value.split(".")
    return date(int(year), int(month), int(day))


def _parse_row(row) -> MeterReading:
    cells = row.find_all("td", recursive=False)
    if len(cells) < 4:
        raise ValueError("Invalid history row format")

    reading_date = _parse_reading_date(cells[0].get_text(strip=True))
    zone_text = cells[1].get_text(strip=True)
    values = [int(text) for text in re.findall(r"\d+", cells[2].get_text())]
    transmitted_by = cells[3].get_text(strip=True)

    if SINGLE_TARIFF_MARKER in zone_text:
        if len(values) < 1:
            raise ValueError("Single-tariff value not found in history row")
        t1, t2 = values[0], None
    else:
        if len(values) < 2:
            raise ValueError("T1/T2 values not found in history row")
        t1, t2 = values[0], values[1]

    return MeterReading(
        t1=t1,
        t2=t2,
        reading_date=reading_date,
        transmitted_by=transmitted_by,
    )


def parse_latest_reading(raw: str) -> MeterReading:
    table_html = extract_table_html(raw)
    soup = BeautifulSoup(table_html, "lxml")
    row = soup.find("tr")
    if not row:
        raise ValueError("History table is empty")

    reading = _parse_row(row)
    logger.debug(
        "Parsed reading: date=%s t1=%s t2=%s transmitted_by=%s",
        reading.reading_date,
        reading.t1,
        reading.t2,
        reading.transmitted_by,
    )
    return reading
