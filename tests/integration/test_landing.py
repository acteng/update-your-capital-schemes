from flask.testing import FlaskClient

from tests.integration.pages import LandingPage


def test_index(client: FlaskClient) -> None:
    response = client.get("/")

    assert LandingPage(response.text).header == "Schemes"
