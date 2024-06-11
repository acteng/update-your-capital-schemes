from flask.testing import FlaskClient


class TestHttpSecurity:
    def test_strict_transport_security(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 200 and response.headers.get("Strict-Transport-Security") == "max-age=31536000"
