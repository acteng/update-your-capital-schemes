from flask.testing import FlaskClient


class TestHttpSecurity:
    def test_strict_transport_security(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 200 and response.headers.get("Strict-Transport-Security") == "max-age=31536000"

    def test_content_type_options_nosniff(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert response.status_code == 200 and response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_referrer_policy(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert (
            response.status_code == 200 and response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        )

    def test_content_security_policy(self, client: FlaskClient) -> None:
        response = client.get("/")

        assert (
            response.status_code == 200
            and response.headers.get("Content-Security-Policy")
            == "script-src 'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw=' "
            "'sha256-qlEoMJwhtzSzuQBNcUtKL5nwWlPXO6xVXHxEUboRWW4=' 'self'; "
            "default-src 'self';"
        )
