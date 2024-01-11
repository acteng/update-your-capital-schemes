from schemes.domain.schemes import DataSource, FinancialType


class FinancialTypeMapper:
    _IDS = {
        FinancialType.EXPECTED_COST: 1,
        FinancialType.ACTUAL_COST: 2,
        FinancialType.FUNDING_ALLOCATION: 3,
        FinancialType.SPENT_TO_DATE: 4,
        FinancialType.FUNDING_REQUEST: 5,
    }

    def to_id(self, financial_type: FinancialType) -> int:
        return self._IDS[financial_type]

    def to_domain(self, id_: int) -> FinancialType:
        return {value: key for key, value in self._IDS.items()}[id_]


class DataSourceMapper:
    _IDS = {
        DataSource.PULSE_5: 1,
        DataSource.PULSE_6: 2,
        DataSource.ATF4_BID: 3,
        DataSource.ATF3_BID: 4,
        DataSource.INSPECTORATE_REVIEW: 5,
        DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW: 6,
        DataSource.ATE_PUBLISHED_DATA: 7,
        DataSource.CHANGE_CONTROL: 8,
        DataSource.ATF4E_BID: 9,
        DataSource.ATF4E_MODERATION: 10,
        DataSource.PULSE_2023_24_Q2: 11,
        DataSource.INITIAL_SCHEME_LIST: 12,
    }

    def to_id(self, data_source: DataSource) -> int:
        return self._IDS[data_source]

    def to_domain(self, id_: int) -> DataSource:
        return {value: key for key, value in self._IDS.items()}[id_]
