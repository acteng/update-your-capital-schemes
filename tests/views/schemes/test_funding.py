from datetime import datetime

import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialRevision, FinancialType, SchemeFunding
from schemes.views.schemes.funding import ChangeSpendToDateContext, ChangeSpendToDateForm, SchemeFundingContext
from tests.builders import build_scheme


class TestSchemeFundingContext:
    def test_from_domain_sets_funding_allocation(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.funding_allocation == 100_000

    def test_from_domain_sets_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.spend_to_date == 50_000

    def test_from_domain_sets_allocation_still_to_spend(self) -> None:
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=110_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.allocation_still_to_spend == 60_000


@pytest.mark.usefixtures("app")
class TestChangeSpendToDateContext:
    def test_from_domain(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")
        scheme.funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=40_000,
                source=DataSource.ATF4_BID,
            ),
        )

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
        funding = SchemeFunding()
        funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        form = ChangeSpendToDateForm.from_domain(funding)

        assert form.amount.data == 50_000 and form.max_amount == 100_000

    def test_from_domain_when_minimal(self) -> None:
        funding = SchemeFunding()

        form = ChangeSpendToDateForm.from_domain(funding)

        assert form.amount.data is None and form.max_amount == 0

    def test_update_domain(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "60000")]))
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(funding, now=datetime(2020, 2, 1))

        financial_revision1, financial_revision2 = funding.financial_revisions
        assert financial_revision1.id == 1 and financial_revision1.effective.date_to == datetime(2020, 2, 1)
        assert (
            financial_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and financial_revision2.type == FinancialType.SPEND_TO_DATE
            and financial_revision2.amount == 60_000
            and financial_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_update_domain_with_zero_amount(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "0")]))
        funding = SchemeFunding()

        form.update_domain(funding, now=datetime(2020, 2, 1))

        assert funding.financial_revisions[0].amount == 0

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
