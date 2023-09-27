from flask.testing import FlaskClient

from tests.integration.pages import HomePage


def test_index(client: FlaskClient) -> None:
    response = client.get("/home/")

    assert HomePage(response.text).header == "Home"
