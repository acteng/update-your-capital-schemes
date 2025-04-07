import pytest
from playwright.sync_api import Page

from tests.e2e.api_client import ApiClient
from tests.e2e.api_client import AuthorityRepr as ApiAuthorityRepr
from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_review(app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.set_clock("2023-04-24T13:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(
        ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
    )
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            authority_reviews=[AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid")],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    schemes_page = SchemePage.open(page, id_=1).review.form.check_up_to_date().confirm()

    assert schemes_page.success_notification.heading == "Wirral Package has been reviewed"
    assert schemes_page.schemes["ATE00001"].last_reviewed == "24 Apr 2023"
    assert app_client.get_scheme(id_=1).authority_reviews == [
        AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid"),
        AuthorityReviewRepr(id=2, review_date="2023-04-24T13:00:00", source="authority update"),
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_cannot_review_when_error(
    app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    app_client.set_clock("2023-04-24T13:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(
        ApiAuthorityRepr(abbreviation="LIV", fullName="Liverpool City Region Combined Authority")
    )
    app_client.add_users("LIV", UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_abbreviation="LIV",
            authority_reviews=[AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid")],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1).review.form.confirm_when_error()

    assert scheme_page.title == "Error: Wirral Package - Update your capital schemes - Active Travel England - GOV.UK"
    assert list(scheme_page.errors) == ["Confirm this scheme is up-to-date"]
    assert (
        scheme_page.review.form.up_to_date.is_errored
        and scheme_page.review.form.up_to_date.error == "Error: Confirm this scheme is up-to-date"
        and not scheme_page.review.form.up_to_date.value
    )
    assert app_client.get_scheme(id_=1).authority_reviews == [
        AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid"),
    ]
