from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SWEDEN_TZ = ZoneInfo("Europe/Stockholm")


def make_start_ts(year: int, month: int, day: int, hour: int, minute: int) -> int:
    dt = datetime(year, month, day, hour, minute, tzinfo=SWEDEN_TZ)
    return int(dt.timestamp())


def next_weekday(weekday: int, hour: int, minute: int) -> int:
    now = datetime.now(SWEDEN_TZ)

    days_ahead = weekday - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    next_day = now + timedelta(days=days_ahead)

    event_time = next_day.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    return int(event_time.timestamp())