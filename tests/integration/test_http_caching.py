from flask.testing import FlaskClient


class TestHttpCaching:
    def test_views_are_not_stored(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.headers.get("Cache-Control") == "no-store"

    def test_static_resources_are_cached_publicly_for_one_hour(self, client: FlaskClient) -> None:
        response = client.get("/static/application.min.css")

        assert response.headers.get("Cache-Control") == "public, max-age=3600"
