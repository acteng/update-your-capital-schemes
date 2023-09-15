from flask.testing import FlaskClient


def test_index(client: FlaskClient) -> None:
    response = client.get("/")

    assert "<h1>Schemes</h1>" in response.text
