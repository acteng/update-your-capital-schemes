from flask.testing import FlaskClient


def test_index(client: FlaskClient) -> None:
    response = client.get("/")

    assert "<p>Hello, World!</p>" in response.text
