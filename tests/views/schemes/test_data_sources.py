import pytest

from schemes.domain.schemes import DataSource
from schemes.views.schemes.data_sources import DataSourceRepr


@pytest.mark.parametrize(
    "data_source, data_source_repr",
    [
        (DataSource.PULSE_5, "Pulse 5"),
        (DataSource.PULSE_6, "Pulse 6"),
        (DataSource.ATF4_BID, "ATF4 Bid"),
        (DataSource.ATF3_BID, "ATF3 Bid"),
        (DataSource.INSPECTORATE_REVIEW, "Inspectorate Review"),
        (DataSource.REGIONAL_MANAGER_REQUEST, "Regional Manager Request"),
        (DataSource.INVESTMENT_TEAM_REQUEST, "Investment Team Request"),
        (DataSource.ATE_PUBLISHED_DATA, "ATE Published Data"),
        (DataSource.CHANGE_CONTROL, "Change Control"),
        (DataSource.ATF4E_BID, "ATF4e Bid"),
        (DataSource.ATF4E_MODERATION, "ATF4e Moderation"),
        (DataSource.PULSE_2023_24_Q2, "Pulse 2023/24 Q2"),
        (DataSource.PULSE_2023_24_Q3, "Pulse 2023/24 Q3"),
        (DataSource.PULSE_2023_24_Q4, "Pulse 2023/24 Q4"),
        (DataSource.INITIAL_SCHEME_LIST, "Initial Scheme List"),
        (DataSource.AUTHORITY_UPDATE, "Authority Update"),
        (DataSource.UNKNOWN, "Unknown"),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, "Pulse 2023/24 Q2 Data Cleanse"),
        (DataSource.PULSE_2023_24_Q3_DATA_CLEANSE, "Pulse 2023/24 Q3 Data Cleanse"),
        (DataSource.LUF_SCHEME_LIST, "LUF Scheme List"),
        (DataSource.LUF_QUARTERLY_UPDATE, "LUF Quarterly Update"),
        (DataSource.CRSTS_SCHEME_LIST, "CRSTS Scheme List"),
        (DataSource.CRSTS_QUARTERLY_UPDATE, "CRSTS Quarterly Update"),
    ],
)
class TestDataSourceRepr:
    def test_from_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr.from_domain(data_source).value == data_source_repr

    def test_to_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr(data_source_repr).to_domain() == data_source
