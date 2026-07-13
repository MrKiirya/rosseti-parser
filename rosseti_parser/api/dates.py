import calendar
from datetime import date


def format_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def month_ago(d: date) -> date:
    month = d.month - 1 or 12
    year = d.year if d.month > 1 else d.year - 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
