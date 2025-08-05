from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_LOCAL_TIMEZONE = ZoneInfo("Europe/London")


def zoned_to_local(zoned: datetime) -> datetime:
    return zoned.astimezone(_LOCAL_TIMEZONE).replace(tzinfo=None)


def local_to_zoned(local: datetime) -> datetime:
    return local.replace(tzinfo=_LOCAL_TIMEZONE).astimezone(timezone.utc)
