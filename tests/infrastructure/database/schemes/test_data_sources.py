import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.infrastructure.database.schemes.data_sources import DataSourceMapper


@pytest.mark.parametrize(
    "data_source, id_",
    [
        (DataSource.PULSE_5, 1),
        (DataSource.PULSE_6, 2),
        (DataSource.ATF4_BID, 3),
        (DataSource.ATF3_BID, 4),
        (DataSource.INSPECTORATE_REQUEST, 5),
        (DataSource.REGIONAL_TEAM_REQUEST, 6),
        (DataSource.INVESTMENT_TEAM_REQUEST, 7),
        (DataSource.ATE_PUBLISHED_DATA, 8),
        (DataSource.CHANGE_CONTROL, 9),
        (DataSource.ATF4E_BID, 10),
        (DataSource.ATF4E_MODERATION, 11),
        (DataSource.PULSE_2023_24_Q2, 12),
        (DataSource.PULSE_2023_24_Q3, 13),
        (DataSource.PULSE_2023_24_Q4, 14),
        (DataSource.INITIAL_SCHEME_LIST, 15),
        (DataSource.AUTHORITY_UPDATE, 16),
        (DataSource.UNKNOWN, 17),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, 18),
        (DataSource.PULSE_2023_24_Q3_DATA_CLEANSE, 19),
        (DataSource.LUF_SCHEME_LIST, 20),
        (DataSource.LUF_QUARTERLY_UPDATE, 21),
        (DataSource.CRSTS_SCHEME_LIST, 22),
        (DataSource.CRSTS_QUARTERLY_UPDATE, 23),
        (DataSource.MRN_SCHEME_LIST, 24),
        (DataSource.MRN_QUARTERLY_UPDATE, 25),
    ],
)
class TestDataSourceMapper:
    def test_to_id(self, data_source: DataSource, id_: int) -> None:
        assert DataSourceMapper().to_id(data_source) == id_

    def test_to_domain(self, data_source: DataSource, id_: int) -> None:
        assert DataSourceMapper().to_domain(id_) == data_source
