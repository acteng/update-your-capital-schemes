from enum import Enum
from typing import Self

from schemes.domain.schemes.data_sources import DataSource


class DataSourceModel(str, Enum):
    PULSE_5 = "Pulse 5"
    PULSE_6 = "Pulse 6"
    ATF4_BID = "ATF4 bid"
    ATF3_BID = "ATF3 bid"
    INSPECTORATE_REQUEST = "Inspectorate request"
    REGIONAL_TEAM_REQUEST = "Regional Team request"
    INVESTMENT_TEAM_REQUEST = "Investment Team request"
    ATE_PUBLISHED_DATA = "ATE published data"
    CHANGE_CONTROL = "change control"
    ATF4E_BID = "ATF4e bid"
    ATF4E_MODERATION = "ATF4e moderation"
    PULSE_2023_24_Q2 = "Pulse 2023/24 Q2"
    PULSE_2023_24_Q3 = "Pulse 2023/24 Q3"
    PULSE_2023_24_Q4 = "Pulse 2023/24 Q4"
    INITIAL_SCHEME_LIST = "initial scheme list"
    AUTHORITY_UPDATE = "authority update"
    UNKNOWN = "unknown"
    PULSE_2023_24_Q2_DATA_CLEANSE = "Pulse 2023/24 Q2 data cleanse"
    PULSE_2023_24_Q3_DATA_CLEANSE = "Pulse 2023/24 Q3 data cleanse"
    LUF_SCHEME_LIST = "LUF scheme list"
    LUF_QUARTERLY_UPDATE = "LUF quarterly update"
    CRSTS_SCHEME_LIST = "CRSTS scheme list"
    CRSTS_QUARTERLY_UPDATE = "CRSTS quarterly update"
    MRN_SCHEME_LIST = "MRN scheme list"
    MRN_QUARTERLY_UPDATE = "MRN quarterly update"
    CATF_SCHEME_SUBMISSION = "CATF scheme submission"

    @classmethod
    def from_domain(cls, data_source: DataSource) -> Self:
        return cls[data_source.name]

    def to_domain(self) -> DataSource:
        return DataSource[self.name]
