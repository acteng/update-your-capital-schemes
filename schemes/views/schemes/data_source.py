from __future__ import annotations

from enum import Enum, unique

from schemes.dicts import inverse_dict
from schemes.domain.schemes import DataSource


@unique
class DataSourceRepr(Enum):
    PULSE_5 = "Pulse 5"
    PULSE_6 = "Pulse 6"
    ATF4_BID = "ATF4 Bid"
    ATF3_BID = "ATF3 Bid"
    INSPECTORATE_REVIEW = "Inspectorate Review"
    REGIONAL_MANAGER_REQUEST = "Regional Manager Request"
    INVESTMENT_TEAM_REQUEST = "Investment Team Request"
    ATE_PUBLISHED_DATA = "ATE Published Data"
    CHANGE_CONTROL = "Change Control"
    ATF4E_BID = "ATF4e Bid"
    ATF4E_MODERATION = "ATF4e Moderation"
    PULSE_2023_24_Q2 = "Pulse 2023/24 Q2"
    PULSE_2023_24_Q3 = "Pulse 2023/24 Q3"
    PULSE_2023_24_Q4 = "Pulse 2023/24 Q4"
    INITIAL_SCHEME_LIST = "Initial Scheme List"
    AUTHORITY_UPDATE = "Authority Update"
    PULSE_2023_24_Q2_DATA_CLEANSE = "Pulse 2023/24 Q2 Data Cleanse"

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
            DataSource.INSPECTORATE_REVIEW: DataSourceRepr.INSPECTORATE_REVIEW,
            DataSource.REGIONAL_MANAGER_REQUEST: DataSourceRepr.REGIONAL_MANAGER_REQUEST,
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
            DataSource.PULSE_2023_24_Q2_DATA_CLEANSE: DataSourceRepr.PULSE_2023_24_Q2_DATA_CLEANSE,
        }
