from flask.testing import FlaskClient

from tests.integration.pages import HomePage


def test_index(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "user@domain.com"}

    response = client.get("/home")

    assert HomePage(response.text).header == "Home"
