from datetime import datetime

import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    DataSource,
    FinancialRevision,
    FinancialType,
    Scheme,
    SchemeFunding,
)
from schemes.views.schemes.data_source import DataSourceRepr
from schemes.views.schemes.funding import (
    BidStatusRepr,
    BidStatusRevisionRepr,
    ChangeSpendToDateContext,
    ChangeSpendToDateForm,
    FinancialRevisionRepr,
    FinancialTypeRepr,
    SchemeFundingContext,
)


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

    def test_from_domain_sets_change_control_adjustment(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=10_000,
                source=DataSource.CHANGE_CONTROL,
            )
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.change_control_adjustment == 10_000

    def test_from_domain_sets_spend_to_date(self) -> None:
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
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
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeFundingContext.from_domain(funding)

        assert context.allocation_still_to_spend == 60_000


@pytest.mark.usefixtures("app")
class TestChangeSpendToDateContext:
    def test_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
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
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=10_000,
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=40_000,
                source=DataSource.ATF4_BID,
            ),
        )

        context = ChangeSpendToDateContext.from_domain(scheme)

        assert (
            context.id == 1
            and context.funding_allocation == 100_000
            and context.change_control_adjustment == 10_000
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
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=10_000,
                source=DataSource.CHANGE_CONTROL,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )

        form = ChangeSpendToDateForm.from_domain(funding)

        assert form.amount.data == 50_000 and form.max_amount == 110_000

    def test_update_domain(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "60000")]))
        funding = SchemeFunding()
        funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )

        form.update_domain(funding, now=datetime(2020, 2, 1))

        financial_revision1: FinancialRevision
        financial_revision2: FinancialRevision
        financial_revision1, financial_revision2 = funding.financial_revisions
        assert financial_revision1.id == 1 and financial_revision1.effective.date_to == datetime(2020, 2, 1)
        assert (
            financial_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and financial_revision2.type == FinancialType.SPENT_TO_DATE
            and financial_revision2.amount == 60_000
            and financial_revision2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_update_domain_with_zero_amount(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "0")]))
        funding = SchemeFunding()

        form.update_domain(funding, now=datetime(2020, 2, 1))

        assert funding.financial_revisions[0].amount == 0

    def test_no_errors_when_valid(self) -> None:
        form = ChangeSpendToDateForm(
            max_amount=110_000, formdata=MultiDict([("csrf_token", generate_csrf()), ("amount", "50000")])
        )

        form.validate()

        assert not form.errors

    def test_amount_is_required(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "")]))

        form.validate()

        assert "Enter spend to date" in form.errors["amount"]

    def test_amount_is_an_integer(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "x")]))

        form.validate()

        assert "Spend to date must be a number" in form.errors["amount"]

    def test_amount_can_be_zero(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "0")]))

        form.validate()

        assert "amount" not in form.errors

    def test_amount_cannot_be_negative(self) -> None:
        form = ChangeSpendToDateForm(max_amount=0, formdata=MultiDict([("amount", "-100")]))

        form.validate()

        assert "Spend to date must be £0 or more" in form.errors["amount"]

    def test_amount_can_be_adjusted_funding_allocation(self) -> None:
        form = ChangeSpendToDateForm(max_amount=110_000, formdata=MultiDict([("amount", "110000")]))

        form.validate()

        assert "amount" not in form.errors

    def test_amount_cannot_exceed_adjusted_funding_allocation(self) -> None:
        form = ChangeSpendToDateForm(max_amount=110_000, formdata=MultiDict([("amount", "120000")]))

        form.validate()

        assert "Spend to date must be £110,000 or less" in form.errors["amount"]


class TestBidStatusRevisionRepr:
    def test_from_domain(self) -> None:
        bid_status_revision = BidStatusRevision(
            id_=2, effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)), status=BidStatus.FUNDED
        )

        bid_status_revision_repr = BidStatusRevisionRepr.from_domain(bid_status_revision)

        assert bid_status_revision_repr == BidStatusRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            status=BidStatusRepr.FUNDED,
        )

    def test_from_domain_when_no_effective_date_to(self) -> None:
        bid_status_revision = BidStatusRevision(
            id_=2, effective=DateRange(datetime(2020, 1, 1, 12), None), status=BidStatus.FUNDED
        )

        bid_status_revision_repr = BidStatusRevisionRepr.from_domain(bid_status_revision)

        assert bid_status_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        bid_status_revision_repr = BidStatusRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            status=BidStatusRepr.FUNDED,
        )

        bid_status_revision = bid_status_revision_repr.to_domain()

        assert (
            bid_status_revision.id == 1
            and bid_status_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and bid_status_revision.status == BidStatus.FUNDED
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        bid_status_revision_repr = BidStatusRevisionRepr(
            id=1, effective_date_from="2020-01-01T12:00:00", effective_date_to=None, status=BidStatusRepr.FUNDED
        )

        bid_status_revision = bid_status_revision_repr.to_domain()

        assert bid_status_revision.effective.date_to is None


@pytest.mark.parametrize(
    "bid_status, bid_status_repr",
    [
        (BidStatus.SUBMITTED, "submitted"),
        (BidStatus.FUNDED, "funded"),
        (BidStatus.NOT_FUNDED, "not funded"),
        (BidStatus.SPLIT, "split"),
        (BidStatus.DELETED, "deleted"),
    ],
)
class TestBidStatusRepr:
    def test_from_domain(self, bid_status: BidStatus, bid_status_repr: str) -> None:
        assert BidStatusRepr.from_domain(bid_status).value == bid_status_repr

    def test_to_domain(self, bid_status: BidStatus, bid_status_repr: str) -> None:
        assert BidStatusRepr(bid_status_repr).to_domain() == bid_status


class TestFinancialRevisionRepr:
    def test_from_domain(self) -> None:
        financial_revision = FinancialRevision(
            id_=2,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        financial_revision_repr = FinancialRevisionRepr.from_domain(financial_revision)

        assert financial_revision_repr == FinancialRevisionRepr(
            id=2,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

    def test_from_domain_when_no_effective_date_to(self) -> None:
        financial_revision = FinancialRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            type_=FinancialType.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSource.ATF4_BID,
        )

        financial_revision_repr = FinancialRevisionRepr.from_domain(financial_revision)

        assert financial_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert (
            financial_revision.id == 1
            and financial_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and financial_revision.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision.amount == 100_000
            and financial_revision.source == DataSource.ATF4_BID
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            id=1,
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type=FinancialTypeRepr.FUNDING_ALLOCATION,
            amount=100_000,
            source=DataSourceRepr.ATF4_BID,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.effective.date_to is None


@pytest.mark.parametrize(
    "financial_type, financial_type_repr",
    [
        (FinancialType.EXPECTED_COST, "expected cost"),
        (FinancialType.ACTUAL_COST, "actual cost"),
        (FinancialType.FUNDING_ALLOCATION, "funding allocation"),
        (FinancialType.SPENT_TO_DATE, "spent to date"),
        (FinancialType.FUNDING_REQUEST, "funding request"),
    ],
)
class TestFinancialTypeRepr:
    def test_from_domain(self, financial_type: FinancialType, financial_type_repr: str) -> None:
        assert FinancialTypeRepr.from_domain(financial_type).value == financial_type_repr

    def test_to_domain(self, financial_type: FinancialType, financial_type_repr: str) -> None:
        assert FinancialTypeRepr(financial_type_repr).to_domain() == financial_type
