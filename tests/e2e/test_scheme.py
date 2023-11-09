import pytest
from flask import Flask
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, SchemeRepr, UserRepr
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme(app_client: AppClient, oidc_client: OidcClient, app: Flask, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(1, SchemeRepr(id=1, name="Wirral Package", type="construction"))
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage(app, page).open(1)

    assert scheme_page.reference_and_name == "ATE00001 - Wirral Package"
    assert scheme_page.scheme_type == "Construction"
