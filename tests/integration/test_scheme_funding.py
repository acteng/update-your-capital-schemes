from datetime import datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    DataSource,
    FinancialRevision,
    FinancialType,
    Scheme,
    SchemeRepository,
)
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.pages import ChangeSpendToDatePage, SchemePage


class TestSchemeFunding:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_minimal_funding(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.funding.funding_allocation == ""
            and scheme_page.funding.change_control_adjustment == ""
            and scheme_page.funding.spend_to_date == ""
            and scheme_page.funding.allocation_still_to_spend == "£0"
        )

    def test_scheme_shows_funding(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
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
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.funding.funding_allocation == "£100,000"
            and scheme_page.funding.change_control_adjustment == "£10,000"
            and scheme_page.funding.spend_to_date == "£50,000"
            and scheme_page.funding.allocation_still_to_spend == "£60,000"
        )

    def test_scheme_shows_zero_funding(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=0,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=0,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=0,
                source=DataSource.CHANGE_CONTROL,
            ),
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert (
            scheme_page.funding.funding_allocation == "£0"
            and scheme_page.funding.change_control_adjustment == "£0"
            and scheme_page.funding.spend_to_date == "£0"
            and scheme_page.funding.allocation_still_to_spend == "£0"
        )

    def test_scheme_shows_change_spend_to_date(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.funding.change_spend_to_date_url == "/schemes/1/spend-to-date"

    def test_spend_to_date_form_shows_back(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert change_spend_to_date_page.back_url == "/schemes/1"

    def test_spend_to_date_form_shows_funding_summary(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
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
        )
        schemes.add(scheme)

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert (
            change_spend_to_date_page.funding_summary
            == "This scheme has £100,000 of funding allocation and £10,000 of change control adjustment."
        )

    def test_spend_to_date_form_shows_minimal_funding_summary(
        self, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert (
            change_spend_to_date_page.funding_summary
            == "This scheme has no funding allocation and no change control adjustment."
        )

    def test_spend_to_date_form_shows_amount(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert change_spend_to_date_page.title == "Update your capital schemes - Active Travel England - GOV.UK"
        assert change_spend_to_date_page.form.amount.value == "50000"

    def test_spend_to_date_form_shows_zero_amount(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=0,
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert change_spend_to_date_page.form.amount.value == "0"

    def test_spend_to_date_form_shows_empty_amount(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert not change_spend_to_date_page.form.amount.value

    def test_spend_to_date_form_shows_confirm(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert change_spend_to_date_page.form.confirm_url == "/schemes/1/spend-to-date"

    def test_spend_to_date_form_shows_cancel(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage.open(client, id_=1)

        assert change_spend_to_date_page.form.cancel_url == "/schemes/1"

    def test_cannot_spend_to_date_form_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        forbidden_page = ChangeSpendToDatePage.open_when_unauthorized(client, id_=2)

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    def test_spend_to_date_updates_spend_to_date(
        self, clock: Clock, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        clock.now = datetime(2020, 2, 1, 13)
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )
        schemes.add(scheme)

        client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

        actual_scheme = schemes.get(1)
        assert actual_scheme
        financial_revision1: FinancialRevision
        financial_revision2: FinancialRevision
        financial_revision3: FinancialRevision
        financial_revision1, financial_revision2, financial_revision3 = actual_scheme.funding.financial_revisions
        assert financial_revision2.id == 2 and financial_revision2.effective.date_to == datetime(2020, 2, 1, 13)
        assert (
            financial_revision3.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and financial_revision3.type == FinancialType.SPENT_TO_DATE
            and financial_revision3.amount == 60_000
            and financial_revision3.source == DataSource.AUTHORITY_UPDATE
        )

    def test_spend_to_date_shows_scheme(self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        response = client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

        assert response.status_code == 302 and response.location == "/schemes/1"

    def test_cannot_spend_to_date_when_error(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPENT_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )
        schemes.add(scheme)

        change_spend_to_date_page = ChangeSpendToDatePage(
            client.post("/schemes/1/spend-to-date", data={"csrf_token": csrf_token, "amount": ""})
        )

        assert change_spend_to_date_page.title == "Error: Update your capital schemes - Active Travel England - GOV.UK"
        assert change_spend_to_date_page.errors and list(change_spend_to_date_page.errors) == ["Enter spend to date"]
        assert (
            change_spend_to_date_page.form.amount.is_errored
            and change_spend_to_date_page.form.amount.error == "Error: Enter spend to date"
            and change_spend_to_date_page.form.amount.value is None
        )
        actual_scheme = schemes.get(1)
        assert actual_scheme
        financial_revision1: FinancialRevision
        (financial_revision1,) = actual_scheme.funding.financial_revisions
        assert (
            financial_revision1.id == 1
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and financial_revision1.type == FinancialType.SPENT_TO_DATE
            and financial_revision1.amount == 50_000
            and financial_revision1.source == DataSource.ATF4_BID
        )

    def test_cannot_spend_to_date_when_no_csrf_token(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage(
            client.post("/schemes/1/spend-to-date", data={"amount": "60000"}, follow_redirects=True)
        )

        assert change_spend_to_date_page.is_visible
        assert (
            change_spend_to_date_page.important_notification
            and change_spend_to_date_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_spend_to_date_when_incorrect_csrf_token(
        self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        change_spend_to_date_page = ChangeSpendToDatePage(
            client.post("/schemes/1/spend-to-date", data={"csrf_token": "x", "amount": "60000"}, follow_redirects=True)
        )

        assert change_spend_to_date_page.is_visible
        assert (
            change_spend_to_date_page.important_notification
            and change_spend_to_date_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_spend_to_date_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        response = client.post("/schemes/2/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

        assert response.status_code == 403
