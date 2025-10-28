import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialType
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.schemes.financials import CapitalSchemeFinancialModel, FinancialTypeModel


class TestFinancialTypeModel:
    @pytest.mark.parametrize(
        "type_model, expected_type",
        [
            (FinancialTypeModel.EXPECTED_COST, FinancialType.EXPECTED_COST),
            (FinancialTypeModel.ACTUAL_COST, FinancialType.ACTUAL_COST),
            (FinancialTypeModel.FUNDING_ALLOCATION, FinancialType.FUNDING_ALLOCATION),
            (FinancialTypeModel.SPEND_TO_DATE, FinancialType.SPEND_TO_DATE),
            (FinancialTypeModel.FUNDING_REQUEST, FinancialType.FUNDING_REQUEST),
        ],
    )
    def test_to_domain(self, type_model: FinancialTypeModel, expected_type: FinancialType) -> None:
        assert type_model.to_domain() == expected_type


class TestCapitalSchemeFinancialModel:
    def test_to_domain(self) -> None:
        financial_model = CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION, amount=100_000, source=DataSourceModel.ATF4_BID
        )

        financial_revision = financial_model.to_domain()

        assert (
            financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )
