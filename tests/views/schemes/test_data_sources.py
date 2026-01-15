import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.views.schemes.data_sources import DataSourceRepr


@pytest.mark.parametrize(
    "data_source, data_source_repr",
    [
        (DataSource.PULSE_5, "Pulse 5"),
        (DataSource.PULSE_6, "Pulse 6"),
        (DataSource.ATF4_BID, "ATF4 bid"),
        (DataSource.ATF3_BID, "ATF3 bid"),
        (DataSource.INSPECTORATE_REQUEST, "Inspectorate request"),
        (DataSource.REGIONAL_TEAM_REQUEST, "Regional Team request"),
        (DataSource.INVESTMENT_TEAM_REQUEST, "Investment Team request"),
        (DataSource.ATE_PUBLISHED_DATA, "ATE published data"),
        (DataSource.CHANGE_CONTROL, "change control"),
        (DataSource.ATF4E_BID, "ATF4e bid"),
        (DataSource.ATF4E_MODERATION, "ATF4e moderation"),
        (DataSource.PULSE_2023_24_Q2, "Pulse 2023/24 Q2"),
        (DataSource.PULSE_2023_24_Q3, "Pulse 2023/24 Q3"),
        (DataSource.PULSE_2023_24_Q4, "Pulse 2023/24 Q4"),
        (DataSource.INITIAL_SCHEME_LIST, "initial scheme list"),
        (DataSource.AUTHORITY_UPDATE, "authority update"),
        (DataSource.UNKNOWN, "unknown"),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, "Pulse 2023/24 Q2 data cleanse"),
        (DataSource.PULSE_2023_24_Q3_DATA_CLEANSE, "Pulse 2023/24 Q3 data cleanse"),
        (DataSource.LUF_SCHEME_LIST, "LUF scheme list"),
        (DataSource.LUF_QUARTERLY_UPDATE, "LUF quarterly update"),
        (DataSource.CRSTS_SCHEME_LIST, "CRSTS scheme list"),
        (DataSource.CRSTS_QUARTERLY_UPDATE, "CRSTS quarterly update"),
        (DataSource.MRN_SCHEME_LIST, "MRN scheme list"),
        (DataSource.MRN_QUARTERLY_UPDATE, "MRN quarterly update"),
        (DataSource.CATF_SCHEME_SUBMISSION, "CATF scheme submission"),
        (DataSource.IST_SCHEME_LIST, "IST scheme list"),
    ],
)
class TestDataSourceRepr:
    def test_from_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr.from_domain(data_source).value == data_source_repr

    def test_to_domain(self, data_source: DataSource, data_source_repr: str) -> None:
        assert DataSourceRepr(data_source_repr).to_domain() == data_source
