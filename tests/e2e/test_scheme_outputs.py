import pytest
from playwright.sync_api import Page

from tests.e2e.app_client import AppClient, AuthorityRepr, OutputRevisionRepr, UserRepr
from tests.e2e.builders import build_scheme
from tests.e2e.oidc_server.users import StubUser
from tests.e2e.oidc_server.web_client import OidcClient
from tests.e2e.pages import SchemePage


@pytest.mark.usefixtures("live_server", "oidc_server")
def test_scheme_outputs(app_client: AppClient, oidc_client: OidcClient, page: Page) -> None:
    app_client.add_authorities(AuthorityRepr(id=1, name="Liverpool City Region Combined Authority"))
    app_client.add_users(1, UserRepr(email="boardman@example.com"))
    app_client.add_schemes(
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_id=1,
            output_revisions=[
                OutputRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="new segregated cycling facility",
                    measure="miles",
                    value="3.000000",
                    observation_type="planned",
                ),
                OutputRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="improvements to make an existing walking/cycle route safer",
                    measure="number of junctions",
                    value="2.600000",
                    observation_type="planned",
                ),
            ],
        ),
    )
    oidc_client.add_user(StubUser("boardman", "boardman@example.com"))

    scheme_page = SchemePage.open(page, id_=1)

    assert scheme_page.outputs.outputs.to_dicts() == [
        {
            "infrastructure": "New segregated cycling facility",
            "measurement": "Miles",
            "planned": "3",
        },
        {
            "infrastructure": "Improvements to make an existing walking/cycle route safer",
            "measurement": "Number of junctions",
            "planned": "2.6",
        },
    ]
