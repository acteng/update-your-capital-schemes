import pytest

from schemes.domain.schemes import DataSource, FinancialType
from schemes.infrastructure.database.schemes.funding import (
    DataSourceMapper,
    FinancialTypeMapper,
)


@pytest.mark.parametrize(
    "financial_type, id_",
    [
        (FinancialType.EXPECTED_COST, 1),
        (FinancialType.ACTUAL_COST, 2),
        (FinancialType.FUNDING_ALLOCATION, 3),
        (FinancialType.SPENT_TO_DATE, 4),
        (FinancialType.FUNDING_REQUEST, 5),
    ],
)
class TestFinancialTypeMapper:
    def test_to_id(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_id(financial_type) == id_

    def test_to_domain(self, financial_type: FinancialType, id_: int) -> None:
        assert FinancialTypeMapper().to_domain(id_) == financial_type


@pytest.mark.parametrize(
    "data_source, id_",
    [
        (DataSource.PULSE_5, 1),
        (DataSource.PULSE_6, 2),
        (DataSource.ATF4_BID, 3),
        (DataSource.ATF3_BID, 4),
        (DataSource.INSPECTORATE_REVIEW, 5),
        (DataSource.REGIONAL_MANAGER_REQUEST, 6),
        (DataSource.ATE_PUBLISHED_DATA, 7),
        (DataSource.CHANGE_CONTROL, 8),
        (DataSource.ATF4E_BID, 9),
        (DataSource.ATF4E_MODERATION, 10),
        (DataSource.PULSE_2023_24_Q2, 11),
        (DataSource.INITIAL_SCHEME_LIST, 12),
        (DataSource.AUTHORITY_UPDATE, 13),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, 14),
    ],
)
class TestDataSourceMapper:
    def test_to_id(self, data_source: DataSource, id_: int) -> None:
        assert DataSourceMapper().to_id(data_source) == id_

    def test_to_domain(self, data_source: DataSource, id_: int) -> None:
        assert DataSourceMapper().to_domain(id_) == data_source
