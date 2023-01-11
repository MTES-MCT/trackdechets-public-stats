from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_data_date_interval_for_year(year: int = 2022) -> tuple[datetime, datetime]:
    now = datetime.now(tz=ZoneInfo("Europe/Paris"))

    date_interval = (
        datetime(year, 1, 1, tzinfo=ZoneInfo("Europe/Paris")),
        datetime(year, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("Europe/Paris")),
    )
    date_start, date_end = date_interval

    if date_end.year == datetime.utcnow().year:
        max_date: datetime = now - timedelta(days=(now.toordinal() % 7) - 1)
        date_end = max_date.replace(hour=0, minute=0, second=0, microsecond=0)

    return date_start, date_end
