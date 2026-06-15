from datetime import datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus
from schemes.domain.schemes.overview import FundingProgrammes
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.conftest import AsyncFlaskClient
from tests.integration.pages import SchemesPage


class TestSchemes:
    @pytest.fixture(name="auth", autouse=True)
    async def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_abbreviation="LIV"))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    async def test_schemes_shows_title(self, async_client: AsyncFlaskClient) -> None:
        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.title == "Your schemes - Update your capital schemes - Active Travel England - GOV.UK"

    @pytest.mark.parametrize(
        "now, expected_notification_banner",
        [
            (datetime(2020, 4, 24, 12), "You have 7 days left to update your schemes"),
            (datetime(2020, 4, 30, 12), "You have 1 day left to update your schemes"),
            (datetime(2020, 5, 1, 12), "Your scheme updates are overdue"),
        ],
    )
    async def test_schemes_shows_update_schemes_notification(
        self,
        async_client: AsyncFlaskClient,
        clock: Clock,
        now: datetime,
        schemes: SchemeRepository,
        expected_notification_banner: str,
    ) -> None:
        clock.now = now
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF3_BID)
        )
        await schemes.add(scheme)

        schemes_page = await SchemesPage.open(async_client)

        assert (
            schemes_page.important_notification
            and schemes_page.important_notification.heading == expected_notification_banner
        )

    async def test_schemes_does_not_show_notification_when_up_to_date(
        self, async_client: AsyncFlaskClient, clock: Clock, schemes: SchemeRepository
    ) -> None:
        clock.now = datetime(2020, 3, 1)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF3_BID)
        )
        await schemes.add(scheme)

        schemes_page = await SchemesPage.open(async_client)

        assert not schemes_page.important_notification

    async def test_schemes_shows_authority(self, async_client: AsyncFlaskClient) -> None:
        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.heading and schemes_page.heading.caption == "Liverpool City Region Combined Authority"

    async def test_schemes_shows_schemes(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV"),
            build_scheme(id_=2, reference="ATE00002", name="School Streets", authority_abbreviation="LIV"),
            build_scheme(
                id_=3,
                reference="ATE00003",
                name="Runcorn Busway",
                authority_abbreviation="LIV",
                bid_status=BidStatus.SUBMITTED,
            ),
            build_scheme(id_=4, reference="ATE00004", name="Hospital Fields Road", authority_abbreviation="WYO"),
            build_scheme(id_=5, reference="ATE00005", overview_revisions=[]),
        )

        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.schemes
        assert [row.reference for row in schemes_page.schemes] == ["ATE00001", "ATE00002"]
        assert not schemes_page.is_no_schemes_message_visible

    async def test_schemes_shows_minimal_scheme(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(
                id_=1,
                reference="ATE00001",
                name="Wirral Package",
                authority_abbreviation="LIV",
                funding_programme=FundingProgrammes.ATF3,
            )
        )

        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.schemes
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": True,
                "last_reviewed": "",
            }
        ]

    async def test_schemes_shows_scheme(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            funding_programme=FundingProgrammes.ATF3,
        )
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2, 12), source=DataSource.ATF3_BID)
        )
        await schemes.add(scheme)

        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.schemes
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": False,
                "last_reviewed": "2 Jan 2020",
            }
        ]

    async def test_schemes_shows_scheme_needs_review(
        self, clock: Clock, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        clock.now = datetime(2023, 4, 24)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2023, 1, 2), source=DataSource.ATF3_BID)
        )
        await schemes.add(scheme)

        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.schemes
        assert [row.needs_review for row in schemes_page.schemes] == [True]

    async def test_scheme_shows_scheme(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        schemes_page = await SchemesPage.open(async_client)

        assert schemes_page.schemes
        assert schemes_page.schemes["ATE00001"].reference_url == "/schemes/ATE00001"

    async def test_schemes_shows_message_when_no_schemes(self, async_client: AsyncFlaskClient) -> None:
        schemes_page = await SchemesPage.open(async_client)

        assert not schemes_page.schemes
        assert schemes_page.is_no_schemes_message_visible
