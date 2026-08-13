import re
from datetime import UTC, datetime

import pytest

from schemes.infrastructure.api.dates import local_to_zoned, zoned_to_local


def test_zoned_to_local() -> None:
    zoned = datetime(2020, 6, 1, 12, tzinfo=UTC)

    local = zoned_to_local(zoned)

    assert local == datetime(2020, 6, 1, 13)


def test_zoned_to_local_with_local_date() -> None:
    local = datetime(2020, 6, 1, 13)

    with pytest.raises(ValueError, match="Date and time must include a time zone: 2020-06-01 13:00:00"):
        zoned_to_local(local)


def test_local_to_zoned() -> None:
    local = datetime(2020, 6, 1, 13)

    zoned = local_to_zoned(local)

    assert zoned == datetime(2020, 6, 1, 12, tzinfo=UTC) and zoned.tzinfo == UTC


def test_local_to_zoned_with_zoned_date() -> None:
    zoned = datetime(2020, 6, 1, 12, tzinfo=UTC)

    with pytest.raises(
        ValueError, match=re.escape("Date and time must not include a time zone: 2020-06-01 12:00:00+00:00")
    ):
        local_to_zoned(zoned)
