import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.infrastructure.api.data_sources import DataSourceModel


@pytest.mark.parametrize(
    "source, source_model",
    [
        (DataSource.PULSE_5, DataSourceModel.PULSE_5),
        (DataSource.PULSE_6, DataSourceModel.PULSE_6),
        (DataSource.ATF4_BID, DataSourceModel.ATF4_BID),
        (DataSource.ATF3_BID, DataSourceModel.ATF3_BID),
        (DataSource.INSPECTORATE_REQUEST, DataSourceModel.INSPECTORATE_REQUEST),
        (DataSource.REGIONAL_TEAM_REQUEST, DataSourceModel.REGIONAL_TEAM_REQUEST),
        (DataSource.INVESTMENT_TEAM_REQUEST, DataSourceModel.INVESTMENT_TEAM_REQUEST),
        (DataSource.ATE_PUBLISHED_DATA, DataSourceModel.ATE_PUBLISHED_DATA),
        (DataSource.CHANGE_CONTROL, DataSourceModel.CHANGE_CONTROL),
        (DataSource.ATF4E_BID, DataSourceModel.ATF4E_BID),
        (DataSource.ATF4E_MODERATION, DataSourceModel.ATF4E_MODERATION),
        (DataSource.PULSE_2023_24_Q2, DataSourceModel.PULSE_2023_24_Q2),
        (DataSource.PULSE_2023_24_Q3, DataSourceModel.PULSE_2023_24_Q3),
        (DataSource.PULSE_2023_24_Q4, DataSourceModel.PULSE_2023_24_Q4),
        (DataSource.INITIAL_SCHEME_LIST, DataSourceModel.INITIAL_SCHEME_LIST),
        (DataSource.AUTHORITY_UPDATE, DataSourceModel.AUTHORITY_UPDATE),
        (DataSource.UNKNOWN, DataSourceModel.UNKNOWN),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, DataSourceModel.PULSE_2023_24_Q2_DATA_CLEANSE),
        (DataSource.PULSE_2023_24_Q3_DATA_CLEANSE, DataSourceModel.PULSE_2023_24_Q3_DATA_CLEANSE),
        (DataSource.LUF_SCHEME_LIST, DataSourceModel.LUF_SCHEME_LIST),
        (DataSource.LUF_QUARTERLY_UPDATE, DataSourceModel.LUF_QUARTERLY_UPDATE),
        (DataSource.CRSTS_SCHEME_LIST, DataSourceModel.CRSTS_SCHEME_LIST),
        (DataSource.CRSTS_QUARTERLY_UPDATE, DataSourceModel.CRSTS_QUARTERLY_UPDATE),
        (DataSource.MRN_SCHEME_LIST, DataSourceModel.MRN_SCHEME_LIST),
        (DataSource.MRN_QUARTERLY_UPDATE, DataSourceModel.MRN_QUARTERLY_UPDATE),
        (DataSource.CATF_SCHEME_SUBMISSION, DataSourceModel.CATF_SCHEME_SUBMISSION),
    ],
)
class TestDataSourceModel:
    def test_from_domain(self, source: DataSource, source_model: DataSourceModel) -> None:
        assert DataSourceModel.from_domain(source) == source_model

    def test_to_domain(self, source: DataSource, source_model: DataSourceModel) -> None:
        assert source_model.to_domain() == source
