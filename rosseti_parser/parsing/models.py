from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MeterReading:
    t1: int
    t2: int | None
    reading_date: date
    transmitted_by: str
