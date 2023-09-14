from flask.testing import FlaskClient


def test_index(client: FlaskClient) -> None:
    response = client.get("/")

    assert response.text == "<p>Hello, World!</p>"
