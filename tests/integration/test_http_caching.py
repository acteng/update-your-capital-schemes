from flask.testing import FlaskClient


class TestHttpCaching:
    def test_views_are_not_stored(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.headers.get("Cache-Control") == "no-store"
