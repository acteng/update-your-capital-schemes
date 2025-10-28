import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.infrastructure.api.data_sources import DataSourceModel


class TestDataSourceModel:
    @pytest.mark.parametrize(
        "source_model, expected_source",
        [
            (DataSourceModel.PULSE_5, DataSource.PULSE_5),
            (DataSourceModel.PULSE_6, DataSource.PULSE_6),
            (DataSourceModel.ATF4_BID, DataSource.ATF4_BID),
            (DataSourceModel.ATF3_BID, DataSource.ATF3_BID),
            (DataSourceModel.INSPECTORATE_REQUEST, DataSource.INSPECTORATE_REQUEST),
            (DataSourceModel.REGIONAL_TEAM_REQUEST, DataSource.REGIONAL_TEAM_REQUEST),
            (DataSourceModel.INVESTMENT_TEAM_REQUEST, DataSource.INVESTMENT_TEAM_REQUEST),
            (DataSourceModel.ATE_PUBLISHED_DATA, DataSource.ATE_PUBLISHED_DATA),
            (DataSourceModel.CHANGE_CONTROL, DataSource.CHANGE_CONTROL),
            (DataSourceModel.ATF4E_BID, DataSource.ATF4E_BID),
            (DataSourceModel.ATF4E_MODERATION, DataSource.ATF4E_MODERATION),
            (DataSourceModel.PULSE_2023_24_Q2, DataSource.PULSE_2023_24_Q2),
            (DataSourceModel.PULSE_2023_24_Q3, DataSource.PULSE_2023_24_Q3),
            (DataSourceModel.PULSE_2023_24_Q4, DataSource.PULSE_2023_24_Q4),
            (DataSourceModel.INITIAL_SCHEME_LIST, DataSource.INITIAL_SCHEME_LIST),
            (DataSourceModel.AUTHORITY_UPDATE, DataSource.AUTHORITY_UPDATE),
            (DataSourceModel.UNKNOWN, DataSource.UNKNOWN),
            (DataSourceModel.PULSE_2023_24_Q2_DATA_CLEANSE, DataSource.PULSE_2023_24_Q2_DATA_CLEANSE),
            (DataSourceModel.PULSE_2023_24_Q3_DATA_CLEANSE, DataSource.PULSE_2023_24_Q3_DATA_CLEANSE),
            (DataSourceModel.LUF_SCHEME_LIST, DataSource.LUF_SCHEME_LIST),
            (DataSourceModel.LUF_QUARTERLY_UPDATE, DataSource.LUF_QUARTERLY_UPDATE),
            (DataSourceModel.CRSTS_SCHEME_LIST, DataSource.CRSTS_SCHEME_LIST),
            (DataSourceModel.CRSTS_QUARTERLY_UPDATE, DataSource.CRSTS_QUARTERLY_UPDATE),
            (DataSourceModel.MRN_SCHEME_LIST, DataSource.MRN_SCHEME_LIST),
            (DataSourceModel.MRN_QUARTERLY_UPDATE, DataSource.MRN_QUARTERLY_UPDATE),
        ],
    )
    def test_to_domain(self, source_model: DataSourceModel, expected_source: DataSource) -> None:
        assert source_model.to_domain() == expected_source
