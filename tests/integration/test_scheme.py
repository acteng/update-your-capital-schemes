from datetime import datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.domain.schemes.schemes import SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.builders import build_scheme
from tests.integration.conftest import AsyncFlaskClient
from tests.integration.pages import SchemePage


class TestScheme:
    @pytest.fixture(name="auth", autouse=True)
    async def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_abbreviation="LIV"))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    async def test_scheme_shows_title(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.title == "Wirral Package - Update your capital schemes - Active Travel England - GOV.UK"

    async def test_scheme_shows_back(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.back_url == "/schemes"

    async def test_scheme_shows_authority(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.heading and scheme_page.heading.caption == "Liverpool City Region Combined Authority"

    async def test_scheme_shows_name(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.heading and scheme_page.heading.text == "Wirral Package"

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            pytest.param(datetime(2023, 1, 2), True, id="review before reporting window"),
            pytest.param(datetime(2023, 4, 1), False, id="review during reporting window"),
        ],
    )
    async def test_scheme_shows_needs_review(
        self,
        clock: Clock,
        schemes: SchemeRepository,
        async_client: AsyncFlaskClient,
        review_date: datetime,
        expected_needs_review: bool,
    ) -> None:
        clock.now = datetime(2023, 4, 24)
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID)
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.needs_review == expected_needs_review

    async def test_cannot_scheme_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="WYO", name="West Yorkshire Combined Authority"))
        await schemes.add(
            build_scheme(id_=2, reference="ATE00002", name="Hospital Fields Road", authority_abbreviation="WYO")
        )

        forbidden_page = await SchemePage.open_when_unauthorized(async_client, reference="ATE00002")

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    async def test_cannot_scheme_when_no_authority(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(build_scheme(id_=2, reference="ATE00002", overview_revisions=[]))

        forbidden_page = await SchemePage.open_when_unauthorized(async_client, reference="ATE00002")

        assert forbidden_page.is_visible and forbidden_page.is_forbidden

    async def test_cannot_scheme_when_unknown_scheme(self, async_client: AsyncFlaskClient) -> None:
        not_found_page = await SchemePage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found

    async def test_cannot_scheme_when_not_updateable_scheme(
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

        not_found_page = await SchemePage.open_when_not_found(async_client, reference="ATE00001")

        assert not_found_page.is_visible and not_found_page.is_not_found
