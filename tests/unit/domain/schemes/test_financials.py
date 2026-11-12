import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import (
    FundingProgramme,
    FundingProgrammes,
    SchemeFinancials,
    SchemeFunding,
    SchemeSpend,
)


class TestFundingProgrammes:
    @pytest.mark.parametrize(
        "funding_programme, expected_code",
        [
            (FundingProgrammes.ATF2, "ATF2"),
            (FundingProgrammes.ATF3, "ATF3"),
            (FundingProgrammes.ATF4, "ATF4"),
            (FundingProgrammes.ATF4E, "ATF4e"),
            (FundingProgrammes.ATF5, "ATF5"),
            (FundingProgrammes.CATF, "CATF"),
            (FundingProgrammes.CRSTS, "CRSTS"),
            (FundingProgrammes.IST, "IST"),
            (FundingProgrammes.LUF1, "LUF1"),
            (FundingProgrammes.LUF2, "LUF2"),
            (FundingProgrammes.LUF3, "LUF3"),
            (FundingProgrammes.MRN, "MRN"),
            (FundingProgrammes.OTH, "OTH"),
            (FundingProgrammes.CON, "CON"),
            (FundingProgrammes.NCN, "NCN"),
            (FundingProgrammes.BUS, "BUS"),
        ],
    )
    def test_code(self, funding_programme: FundingProgramme, expected_code: str) -> None:
        assert funding_programme.code == expected_code

    @pytest.mark.parametrize(
        "funding_programme, expected_is_eligible_for_authority_update",
        [
            (FundingProgrammes.ATF2, True),
            (FundingProgrammes.ATF3, True),
            (FundingProgrammes.ATF4, True),
            (FundingProgrammes.ATF4E, True),
            (FundingProgrammes.ATF5, True),
            (FundingProgrammes.CATF, True),
            (FundingProgrammes.CRSTS, False),
            (FundingProgrammes.IST, True),
            (FundingProgrammes.LUF1, False),
            (FundingProgrammes.LUF2, False),
            (FundingProgrammes.LUF3, False),
            (FundingProgrammes.MRN, False),
            (FundingProgrammes.OTH, False),
            (FundingProgrammes.CON, True),
            (FundingProgrammes.NCN, True),
            (FundingProgrammes.BUS, True),
        ],
    )
    def test_is_eligible_for_authority_update(
        self, funding_programme: FundingProgramme, expected_is_eligible_for_authority_update: bool
    ) -> None:
        assert funding_programme.is_eligible_for_authority_update == expected_is_eligible_for_authority_update


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
