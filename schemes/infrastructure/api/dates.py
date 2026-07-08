from datetime import UTC, datetime
from zoneinfo import ZoneInfo

_LOCAL_TIMEZONE = ZoneInfo("Europe/London")


def zoned_to_local(zoned: datetime) -> datetime:
    if not _is_zoned(zoned):
        raise ValueError(f"Date and time must include a time zone: {zoned}")

    return zoned.astimezone(_LOCAL_TIMEZONE).replace(tzinfo=None)


def local_to_zoned(local: datetime) -> datetime:
    if _is_zoned(local):
        raise ValueError(f"Date and time must not include a time zone: {local}")

    return local.replace(tzinfo=_LOCAL_TIMEZONE).astimezone(UTC)


def _is_zoned(date: datetime) -> bool:
    """
    Determines if the specified date includes a time zone.

    In Python this is known as an "aware" date and time (zoned), as opposed to a "naive" date and time (local).

    See: https://docs.python.org/3.13/library/datetime.html#determining-if-an-object-is-aware-or-naive
    """
    tz = date.tzinfo
    return tz is not None and tz.utcoffset(date) is not None
