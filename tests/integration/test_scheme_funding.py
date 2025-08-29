from datetime import datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, FinancialRevision, FinancialType
from schemes.domain.schemes.schemes import SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.conftest import AsyncFlaskClient
from tests.integration.pages import ChangeSpendToDatePage, SchemePage


class TestSchemeFunding:
    @pytest.fixture(name="auth", autouse=True)
    async def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_abbreviation="LIV"))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    async def test_scheme_shows_minimal_funding(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert (
            scheme_page.funding.funding_allocation == ""
            and scheme_page.funding.spend_to_date == ""
            and scheme_page.funding.allocation_still_to_spend == "£0"
        )

    async def test_scheme_shows_funding(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
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
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert (
            scheme_page.funding.funding_allocation == "£100,000"
            and scheme_page.funding.spend_to_date == "£50,000"
            and scheme_page.funding.allocation_still_to_spend == "£50,000"
        )

    async def test_scheme_shows_zero_funding(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
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
                type_=FinancialType.SPEND_TO_DATE,
                amount=0,
                source=DataSource.ATF4_BID,
            ),
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert (
            scheme_page.funding.funding_allocation == "£0"
            and scheme_page.funding.spend_to_date == "£0"
            and scheme_page.funding.allocation_still_to_spend == "£0"
        )

    async def test_scheme_shows_change_spend_to_date(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.funding.change_spend_to_date_url == "/schemes/ATE00001/spend-to-date"

    async def test_spend_to_date_form_shows_title(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert (
            change_spend_to_date_page.title
            == "How much has been spent to date? - Update your capital schemes - Active Travel England - GOV.UK"
        )

    async def test_spend_to_date_form_shows_back(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.back_url == "/schemes/ATE00001"

    async def test_spend_to_date_form_shows_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.heading.caption == "Wirral Package"

    async def test_spend_to_date_form_shows_funding_summary(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.funding.update_financials(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.funding_summary == "This scheme has £100,000 of funding allocation"

    async def test_spend_to_date_form_shows_minimal_funding_summary(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.funding_summary == "This scheme has no funding allocation"

    async def test_spend_to_date_form_shows_amount(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.amount.value == "50000"

    async def test_spend_to_date_form_shows_zero_amount(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=0,
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.amount.value == "0"

    async def test_spend_to_date_form_shows_empty_amount(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert not change_spend_to_date_page.form.amount.value

    async def test_spend_to_date_form_shows_confirm(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.confirm_url == "/schemes/ATE00001/spend-to-date"

    async def test_spend_to_date_form_shows_cancel(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = await ChangeSpendToDatePage.open(async_client, reference="ATE00001")

        assert change_spend_to_date_page.form.cancel_url == "/schemes/ATE00001"

    async def test_cannot_spend_to_date_form_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"))
        await schemes.add(
            build_scheme(id_=2, reference="ATE00002", name="Hospital Fields Road", authority_abbreviation="WYO")
        )

        forbidden_page = await ChangeSpendToDatePage.open_when_unauthorized(async_client, reference="ATE00002")

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    async def test_cannot_spend_to_date_form_when_no_authority(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(build_scheme(id_=2, reference="ATE00002", overview_revisions=[]))

        forbidden_page = await ChangeSpendToDatePage.open_when_unauthorized(async_client, reference="ATE00002")

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    async def test_cannot_spend_to_date_form_when_unknown_scheme(self, async_client: AsyncFlaskClient) -> None:
        not_found_page = await ChangeSpendToDatePage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found

    async def test_cannot_spend_to_date_form_when_not_updateable_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(
                id_=1,
                reference="ATE00001",
                name="Wirral Package",
                authority_abbreviation="LIV",
                bid_status=BidStatus.SUBMITTED,
            )
        )

        not_found_page = await ChangeSpendToDatePage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found

    async def test_spend_to_date_updates_spend_to_date(
        self, clock: Clock, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        clock.now = datetime(2020, 2, 1, 13)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
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
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            ),
        )
        await schemes.add(scheme)

        await async_client.post("/schemes/ATE00001/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

        actual_scheme = await schemes.get("ATE00001")
        assert actual_scheme
        financial_revision1, financial_revision2, financial_revision3 = actual_scheme.funding.financial_revisions
        assert financial_revision2.id == 2 and financial_revision2.effective.date_to == datetime(2020, 2, 1, 13)
        assert (
            financial_revision3.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and financial_revision3.type == FinancialType.SPEND_TO_DATE
            and financial_revision3.amount == 60_000
            and financial_revision3.source == DataSource.AUTHORITY_UPDATE
        )

    async def test_spend_to_date_shows_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        response = await async_client.post(
            "/schemes/ATE00001/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"}
        )

        assert response.status_code == 302 and response.location == "/schemes/ATE00001"

    async def test_cannot_spend_to_date_when_error(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=50_000,
                source=DataSource.ATF4_BID,
            )
        )
        await schemes.add(scheme)

        change_spend_to_date_page = ChangeSpendToDatePage(
            await async_client.post("/schemes/ATE00001/spend-to-date", data={"csrf_token": csrf_token, "amount": ""})
        )

        assert (
            change_spend_to_date_page.title
            == "Error: How much has been spent to date? - Update your capital schemes - Active Travel England - GOV.UK"
        )
        assert change_spend_to_date_page.errors and list(change_spend_to_date_page.errors) == ["Enter spend to date"]
        assert (
            change_spend_to_date_page.form.amount.is_errored
            and change_spend_to_date_page.form.amount.error == "Error: Enter spend to date"
            and change_spend_to_date_page.form.amount.value == ""
        )
        actual_scheme = await schemes.get("ATE00001")
        assert actual_scheme
        (financial_revision1,) = actual_scheme.funding.financial_revisions
        assert (
            financial_revision1.id == 1
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and financial_revision1.type == FinancialType.SPEND_TO_DATE
            and financial_revision1.amount == 50_000
            and financial_revision1.source == DataSource.ATF4_BID
        )

    async def test_cannot_spend_to_date_when_no_csrf_token(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = ChangeSpendToDatePage(
            await async_client.post("/schemes/ATE00001/spend-to-date", data={"amount": "60000"}, follow_redirects=True)
        )

        assert change_spend_to_date_page.is_visible
        assert (
            change_spend_to_date_page.important_notification
            and change_spend_to_date_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    async def test_cannot_spend_to_date_when_incorrect_csrf_token(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        change_spend_to_date_page = ChangeSpendToDatePage(
            await async_client.post(
                "/schemes/ATE00001/spend-to-date", data={"csrf_token": "x", "amount": "60000"}, follow_redirects=True
            )
        )

        assert change_spend_to_date_page.is_visible
        assert (
            change_spend_to_date_page.important_notification
            and change_spend_to_date_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    async def test_cannot_spend_to_date_when_different_authority(
        self,
        authorities: AuthorityRepository,
        schemes: SchemeRepository,
        async_client: AsyncFlaskClient,
        csrf_token: str,
    ) -> None:
        await authorities.add(Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"))
        await schemes.add(
            build_scheme(id_=2, reference="ATE00002", name="Hospital Fields Road", authority_abbreviation="WYO")
        )

        response = await async_client.post(
            "/schemes/ATE00002/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"}
        )

        assert response.status_code == 403

    async def test_cannot_spend_to_date_when_no_authority(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        await schemes.add(build_scheme(id_=2, reference="ATE00002", overview_revisions=[]))

        response = await async_client.post(
            "/schemes/ATE00002/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"}
        )

        assert response.status_code == 403

    def test_cannot_spend_to_date_when_unknown_scheme(self, client: FlaskClient, csrf_token: str) -> None:
        response = client.post("/schemes/ATE00001/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"})

        assert response.status_code == 404

    async def test_cannot_spend_to_date_when_not_updateable_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient, csrf_token: str
    ) -> None:
        await schemes.add(
            build_scheme(
                id_=1,
                reference="ATE00001",
                name="Wirral Package",
                authority_abbreviation="LIV",
                bid_status=BidStatus.SUBMITTED,
            )
        )

        response = await async_client.post(
            "/schemes/ATE00001/spend-to-date", data={"csrf_token": csrf_token, "amount": "60000"}
        )

        assert response.status_code == 404
