from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateRange:
    date_from: datetime
    date_to: datetime | None

    def __post_init__(self) -> None:
        if not (self.date_to is None or self.date_from <= self.date_to):
            raise ValueError(f"From date '{self.date_from}' must not be after to date '{self.date_to}'")
