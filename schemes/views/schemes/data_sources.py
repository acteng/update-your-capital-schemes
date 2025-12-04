from __future__ import annotations

from enum import Enum, unique

from schemes.dicts import inverse_dict
from schemes.domain.schemes.data_sources import DataSource


@unique
class DataSourceRepr(str, Enum):
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
    def from_domain(cls, data_source: DataSource) -> DataSourceRepr:
        return cls._members()[data_source]

    def to_domain(self) -> DataSource:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[DataSource, DataSourceRepr]:
        return {
            DataSource.PULSE_5: DataSourceRepr.PULSE_5,
            DataSource.PULSE_6: DataSourceRepr.PULSE_6,
            DataSource.ATF4_BID: DataSourceRepr.ATF4_BID,
            DataSource.ATF3_BID: DataSourceRepr.ATF3_BID,
            DataSource.INSPECTORATE_REQUEST: DataSourceRepr.INSPECTORATE_REQUEST,
            DataSource.REGIONAL_TEAM_REQUEST: DataSourceRepr.REGIONAL_TEAM_REQUEST,
            DataSource.INVESTMENT_TEAM_REQUEST: DataSourceRepr.INVESTMENT_TEAM_REQUEST,
            DataSource.ATE_PUBLISHED_DATA: DataSourceRepr.ATE_PUBLISHED_DATA,
            DataSource.CHANGE_CONTROL: DataSourceRepr.CHANGE_CONTROL,
            DataSource.ATF4E_BID: DataSourceRepr.ATF4E_BID,
            DataSource.ATF4E_MODERATION: DataSourceRepr.ATF4E_MODERATION,
            DataSource.PULSE_2023_24_Q2: DataSourceRepr.PULSE_2023_24_Q2,
            DataSource.PULSE_2023_24_Q3: DataSourceRepr.PULSE_2023_24_Q3,
            DataSource.PULSE_2023_24_Q4: DataSourceRepr.PULSE_2023_24_Q4,
            DataSource.INITIAL_SCHEME_LIST: DataSourceRepr.INITIAL_SCHEME_LIST,
            DataSource.AUTHORITY_UPDATE: DataSourceRepr.AUTHORITY_UPDATE,
            DataSource.UNKNOWN: DataSourceRepr.UNKNOWN,
            DataSource.PULSE_2023_24_Q2_DATA_CLEANSE: DataSourceRepr.PULSE_2023_24_Q2_DATA_CLEANSE,
            DataSource.PULSE_2023_24_Q3_DATA_CLEANSE: DataSourceRepr.PULSE_2023_24_Q3_DATA_CLEANSE,
            DataSource.LUF_SCHEME_LIST: DataSourceRepr.LUF_SCHEME_LIST,
            DataSource.LUF_QUARTERLY_UPDATE: DataSourceRepr.LUF_QUARTERLY_UPDATE,
            DataSource.CRSTS_SCHEME_LIST: DataSourceRepr.CRSTS_SCHEME_LIST,
            DataSource.CRSTS_QUARTERLY_UPDATE: DataSourceRepr.CRSTS_QUARTERLY_UPDATE,
            DataSource.MRN_SCHEME_LIST: DataSourceRepr.MRN_SCHEME_LIST,
            DataSource.MRN_QUARTERLY_UPDATE: DataSourceRepr.MRN_QUARTERLY_UPDATE,
            DataSource.CATF_SCHEME_SUBMISSION: DataSourceRepr.CATF_SCHEME_SUBMISSION,
        }
