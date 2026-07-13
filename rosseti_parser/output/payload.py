from datetime import datetime

from rosseti_parser.parsing.models import MeterReading

SOURCE = "rosseti"


def build_payload(reading: MeterReading) -> dict:
    payload = {
        "t1": reading.t1,
        "t2": reading.t2,
        "reading_date": reading.reading_date.isoformat(),
        "transmitted_by": reading.transmitted_by,
        "received_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SOURCE,
    }
    return payload
