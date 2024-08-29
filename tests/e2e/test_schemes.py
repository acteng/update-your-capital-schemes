import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemesPage


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestAuthenticated:
    @pytest.fixture(autouse=True)
    def oidc_user(self, oidc_client: OidcClient) -> None:
        oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    def test_schemes(self, app_client: AppClient, page: Page) -> None:
        app_client.set_clock("2023-04-24T12:00:00")
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        app_client.add_schemes(
            build_scheme(
                id_=1,
                name="Wirral Package",
                authority_id=1,
                funding_programme="ATF3",
                authority_reviews=[AuthorityReviewRepr(id=1, review_date="2020-01-02", source="ATF3 Bid")],
            ),
            build_scheme(
                id_=2,
                name="School Streets",
                authority_id=1,
                funding_programme="ATF4",
                authority_reviews=[AuthorityReviewRepr(id=2, review_date="2020-01-03", source="ATF4 Bid")],
            ),
        )

        schemes_page = SchemesPage.open(page)

        assert schemes_page.heading.caption == "Liverpool City Region Combined Authority"
        assert schemes_page.schemes.to_dicts() == [
            {
                "reference": "ATE00001",
                "funding_programme": "ATF3",
                "name": "Wirral Package",
                "needs_review": True,
                "last_reviewed": "2 Jan 2020",
            },
            {
                "reference": "ATE00002",
                "funding_programme": "ATF4",
                "name": "School Streets",
                "needs_review": True,
                "last_reviewed": "3 Jan 2020",
            },
        ]

    def test_schemes_when_unauthorized(self, page: Page) -> None:
        forbidden_page = SchemesPage.open_when_unauthorized(page)

        assert forbidden_page.is_visible

    def test_scheme_shows_scheme(self, app_client: AppClient, page: Page) -> None:
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        app_client.add_schemes(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemesPage.open(page).schemes["ATE00001"].open()

        assert scheme_page.heading.text == "Wirral Package"

    def test_schemes_shows_update_schemes_notification(self, app_client: AppClient, page: Page) -> None:
        app_client.set_clock("2023-04-24T12:00:00")
        app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
        app_client.add_users(1, UserRepr(email="boardman@example.com"))
        app_client.add_schemes(
            build_scheme(
                id_=1,
                name="Wirral Package",
                authority_id=1,
                authority_reviews=[AuthorityReviewRepr(id=1, review_date="2023-01-02", source="ATF4 Bid")],
            ),
        )

        schemes_page = SchemesPage.open(page)

        assert schemes_page.important_notification.heading == "You have 7 days left to update your schemes"


@pytest.mark.usefixtures("live_server", "oidc_server")
class TestUnauthenticated:
    def test_schemes_when_unauthenticated(self, page: Page) -> None:
        login_page = SchemesPage.open_when_unauthenticated(page)

        assert login_page.is_visible
