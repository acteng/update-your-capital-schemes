from datetime import datetime

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialRevision, FinancialType
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.financial_types import FinancialTypeModel
from schemes.infrastructure.api.schemes.financials import CapitalSchemeFinancialModel


class TestCapitalSchemeFinancialModel:
    def test_from_domain(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        financial_model = CapitalSchemeFinancialModel.from_domain(financial_revision)

        assert financial_model == CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION, amount=100_000, source=DataSourceModel.ATF4_BID
        )

    def test_to_domain(self) -> None:
        financial_model = CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION, amount=100_000, source=DataSourceModel.ATF4_BID
        )

        financial_revision = financial_model.to_domain()

        assert (
            financial_revision.id is not None
            and financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )
