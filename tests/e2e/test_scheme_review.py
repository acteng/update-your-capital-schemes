import pytest
from flask import Flask
from playwright.async_api import Page

from tests.e2e.api_client import ApiClient, AuthorityModel
from tests.e2e.app_client import AppClient, AuthorityRepr, AuthorityReviewRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.usefixtures("live_server", "oidc_server")
async def test_scheme_review(
    app: Flask, app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    app_client.set_clock("2023-04-24T13:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
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

    scheme_page = await SchemePage.open(page, reference="ATE00001")
    scheme_review_form = await scheme_page.review.form.check_up_to_date()
    schemes_page = await scheme_review_form.confirm()

    assert await schemes_page.success_notification.heading() == "Wirral Package has been reviewed"
    # TODO: reinstate when https://github.com/acteng/update-your-capital-schemes/issues/191 resolved
    if "ATE_URL" not in app.config:
        assert await (await schemes_page.schemes.scheme("ATE00001")).last_reviewed() == "24 Apr 2023"
    assert app_client.get_scheme(reference="ATE00001").authority_reviews == [
        AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid"),
        AuthorityReviewRepr(id=2, review_date="2023-04-24T13:00:00", source="authority update"),
    ]


@pytest.mark.usefixtures("live_server", "oidc_server")
async def test_scheme_cannot_review_when_error(
    app_client: AppClient, api_client: ApiClient, oidc_client: OidcClient, page: Page
) -> None:
    app_client.set_clock("2023-04-24T13:00:00")
    app_client.add_authorities(AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
    api_client.add_authorities(AuthorityModel(abbreviation="LIV", fullName="Liverpool City Region Combined Authority"))
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

    scheme_page = await SchemePage.open(page, reference="ATE00001")
    scheme_page = await scheme_page.review.form.confirm_when_error()

    assert (
        await scheme_page.title()
        == "Error: Wirral Package - Update your capital schemes - Active Travel England - GOV.UK"
    )
    assert [error async for error in scheme_page.errors] == ["Confirm this scheme is up-to-date"]
    assert (
        await scheme_page.review.form.up_to_date.is_errored()
        and await scheme_page.review.form.up_to_date.error() == "Error: Confirm this scheme is up-to-date"
        and not await scheme_page.review.form.up_to_date.value()
    )
    assert app_client.get_scheme(reference="ATE00001").authority_reviews == [
        AuthorityReviewRepr(id=1, review_date="2020-01-02T12:00:00", source="ATF4 bid"),
    ]
