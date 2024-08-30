from schemes.dicts import inverse_dict
from schemes.domain.schemes import DataSource


class DataSourceMapper:
    _IDS = {
        DataSource.PULSE_5: 1,
        DataSource.PULSE_6: 2,
        DataSource.ATF4_BID: 3,
        DataSource.ATF3_BID: 4,
        DataSource.INSPECTORATE_REVIEW: 5,
        DataSource.REGIONAL_MANAGER_REQUEST: 6,
        DataSource.INVESTMENT_TEAM_REQUEST: 7,
        DataSource.ATE_PUBLISHED_DATA: 8,
        DataSource.CHANGE_CONTROL: 9,
        DataSource.ATF4E_BID: 10,
        DataSource.ATF4E_MODERATION: 11,
        DataSource.PULSE_2023_24_Q2: 12,
        DataSource.PULSE_2023_24_Q3: 13,
        DataSource.PULSE_2023_24_Q4: 14,
        DataSource.INITIAL_SCHEME_LIST: 15,
        DataSource.AUTHORITY_UPDATE: 16,
        DataSource.UNKNOWN: 17,
        DataSource.PULSE_2023_24_Q2_DATA_CLEANSE: 18,
        DataSource.PULSE_2023_24_Q3_DATA_CLEANSE: 19,
        DataSource.LUF_SCHEME_LIST: 20,
        DataSource.LUF_QUARTERLY_UPDATE: 21,
        DataSource.CRSTS_SCHEME_LIST: 22,
        DataSource.CRSTS_QUARTERLY_UPDATE: 23,
    }

    def to_id(self, data_source: DataSource) -> int:
        return self._IDS[data_source]

    def to_domain(self, id_: int) -> DataSource:
        return inverse_dict(self._IDS)[id_]
