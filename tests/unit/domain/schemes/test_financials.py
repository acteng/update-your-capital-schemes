from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import SchemeFinancials, SchemeFunding, SchemeSpend
from schemes.domain.schemes.overview import FundingProgrammes


class TestSchemeFunding:
    def test_create(self) -> None:
        funding = SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000)

        assert funding.funding_programme == FundingProgrammes.ATF4 and funding.amount == 100_000


class TestSchemeSpend:
    def test_create(self) -> None:
        spend = SchemeSpend(surrogate_id=1, amount=100_000, source=DataSource.ATF4_BID)

        assert spend.surrogate_id == 1 and spend.amount == 100_000 and spend.source == DataSource.ATF4_BID


class TestSchemeFinancials:
    def test_create(self) -> None:
        financials = SchemeFinancials()

        assert financials.fundings == [] and not financials.spend

    def test_get_fundings_is_copy(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000))

        financials.fundings.clear()

        assert financials.fundings

    def test_update_funding(self) -> None:
        financials = SchemeFinancials()
        funding = SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000)

        financials.update_funding(funding)

        assert financials.fundings == [funding]

    def test_update_fundings(self) -> None:
        financials = SchemeFinancials()
        funding1 = SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000)
        funding2 = SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=20_000)

        financials.update_fundings(funding1, funding2)

        assert financials.fundings == [funding1, funding2]

    def test_update_spend(self) -> None:
        financials = SchemeFinancials()
        spend = SchemeSpend(surrogate_id=1, amount=100_000, source=DataSource.ATF4_BID)

        financials.update_spend(spend)

        assert financials.spend == spend

    def test_update_spend_to_date(self) -> None:
        financials = SchemeFinancials()

        financials.update_spend_to_date(60_000)

        spend = financials.spend
        assert (
            spend
            and spend.surrogate_id is None
            and spend.amount == 60_000
            and spend.source == DataSource.AUTHORITY_UPDATE
        )

    def test_get_funding_allocation_sums_amounts(self) -> None:
        financials = SchemeFinancials()
        financials.update_fundings(
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000),
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=20_000),
        )

        assert financials.funding_allocation == 120_000

    def test_get_funding_allocation_when_no_fundings(self) -> None:
        financials = SchemeFinancials()

        assert financials.funding_allocation is None

    def test_get_spend_to_date(self) -> None:
        financials = SchemeFinancials()
        financials.update_spend(SchemeSpend(surrogate_id=1, amount=100_000, source=DataSource.ATF4_BID))

        assert financials.spend_to_date == 100_000

    def test_get_spend_to_date_when_no_spend(self) -> None:
        financials = SchemeFinancials()

        assert financials.spend_to_date is None

    def test_get_allocation_still_to_spend(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000))
        financials.update_spend(SchemeSpend(surrogate_id=1, amount=50_000, source=DataSource.ATF4_BID))

        assert financials.allocation_still_to_spend == 50_000

    def test_get_allocation_still_to_spend_when_no_funding_allocation(self) -> None:
        financials = SchemeFinancials()
        financials.update_spend(SchemeSpend(surrogate_id=1, amount=50_000, source=DataSource.ATF4_BID))

        assert financials.allocation_still_to_spend == -50_000

    def test_get_allocation_still_to_spend_when_no_spend(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000))

        assert financials.allocation_still_to_spend == 100_000

    def test_get_allocation_still_to_spend_when_no_financials(self) -> None:
        financials = SchemeFinancials()

        assert financials.allocation_still_to_spend == 0
