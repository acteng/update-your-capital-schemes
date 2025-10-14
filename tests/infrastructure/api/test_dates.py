from datetime import UTC, datetime

from schemes.infrastructure.api.dates import local_to_zoned, zoned_to_local


def test_zoned_to_local() -> None:
    zoned = datetime(2020, 6, 1, 12, tzinfo=UTC)

    local = zoned_to_local(zoned)

    assert local == datetime(2020, 6, 1, 13)


def test_local_to_zoned() -> None:
    local = datetime(2020, 6, 1, 13)

    zoned = local_to_zoned(local)

    assert zoned == datetime(2020, 6, 1, 12, tzinfo=UTC) and zoned.tzinfo == UTC
