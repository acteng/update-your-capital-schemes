from flask.testing import FlaskClient

from tests.integration.pages import HomePage


def test_home(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["user"] = {"email": "user@domain.com"}

    home_page = HomePage(client).show()

    assert home_page.visible()
