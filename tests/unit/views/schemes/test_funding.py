import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.financials import SchemeFinancials, SchemeFunding, SchemeSpend
from schemes.domain.schemes.overview import FundingProgrammes
from schemes.views.schemes.funding import ChangeSpendToDateContext, ChangeSpendToDateForm, SchemeFundingContext
from tests.unit.domain.builders import build_scheme


class TestSchemeFundingContext:
    def test_from_domain_sets_funding_allocation(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000, source=DataSource.ATF4_BID)
        )

        context = SchemeFundingContext.from_domain(financials)

        assert context.funding_allocation == 100_000

    def test_from_domain_sets_spend_to_date(self) -> None:
        financials = SchemeFinancials()
        financials.update_spend(SchemeSpend(id_=1, amount=50_000, source=DataSource.ATF4_BID))

        context = SchemeFundingContext.from_domain(financials)

        assert context.spend_to_date == 50_000

    def test_from_domain_sets_allocation_still_to_spend(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=110_000, source=DataSource.ATF4_BID)
        )
        financials.update_spend(SchemeSpend(id_=1, amount=50_000, source=DataSource.ATF4_BID))

        context = SchemeFundingContext.from_domain(financials)

        assert context.allocation_still_to_spend == 60_000


@pytest.mark.usefixtures("app")
class TestChangeSpendToDateContext:
    def test_from_domain(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")
        scheme.financials.update_funding(
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000, source=DataSource.ATF4_BID)
        )
        scheme.financials.update_spend(SchemeSpend(id_=1, amount=40_000, source=DataSource.ATF4_BID))

        context = ChangeSpendToDateContext.from_domain(scheme)

        assert (
            context.reference == "ATE00001"
            and context.name == "Wirral Package"
            and context.funding_allocation == 100_000
            and context.form.amount.data == 40_000
        )


@pytest.mark.usefixtures("app")
class TestChangeSpendToDateForm:
    def test_from_domain(self) -> None:
        financials = SchemeFinancials()
        financials.update_funding(
            SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000, source=DataSource.ATF4_BID)
        )
        financials.update_spend(SchemeSpend(id_=1, amount=50_000, source=DataSource.ATF4_BID))

        form = ChangeSpendToDateForm.from_domain(financials)

        assert form.amount.data == 50_000 and form.max_amount == 100_000

    def test_from_domain_when_minimal(self) -> None:
        financials = SchemeFinancials()

        form = ChangeSpendToDateForm.from_domain(financials)

        assert form.amount.data is None and form.max_amount == 0

    def test_update_domain(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "60000")]))
        financials = SchemeFinancials()
        financials.update_spend(SchemeSpend(id_=1, amount=50_000, source=DataSource.ATF4_BID))

        form.update_domain(financials)

        spend = financials.spend
        assert spend and spend.amount == 60_000 and spend.source == DataSource.AUTHORITY_UPDATE

    def test_update_domain_with_zero_amount(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "0")]))
        financials = SchemeFinancials()

        form.update_domain(financials)

        spend = financials.spend
        assert spend and spend.amount == 0

    def test_validate_when_valid(self) -> None:
        form = ChangeSpendToDateForm(
            max_amount=110_000, formdata=MultiDict([("csrf_token", generate_csrf()), ("amount", "50000")])
        )

        form.validate()

        assert not form.errors

    def test_validate_amount_is_required(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "")]))

        form.validate()

        assert "Enter spend to date" in form.errors["amount"]

    def test_validate_amount_is_an_integer(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "x")]))

        form.validate()

        assert "Spend to date must be a number" in form.errors["amount"]

    def test_validate_amount_can_be_zero(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "0")]))

        form.validate()

        assert "amount" not in form.errors

    def test_validate_amount_cannot_be_negative(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "-100")]))

        form.validate()

        assert "Spend to date must be £0 or more" in form.errors["amount"]

    def test_validate_amount_can_be_adjusted_funding_allocation(self) -> None:
        form = ChangeSpendToDateForm(max_amount=110_000, formdata=MultiDict([("amount", "110000")]))

        form.validate()

        assert "amount" not in form.errors

    def test_validate_amount_cannot_exceed_adjusted_funding_allocation(self) -> None:
        form = ChangeSpendToDateForm(max_amount=110_000, formdata=MultiDict([("amount", "120000")]))

        form.validate()

        assert "Spend to date must be £110,000 or less" in form.errors["amount"]
