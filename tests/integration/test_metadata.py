from flask.testing import FlaskClient

from tests.integration.pages import StartPage


class TestMetadata:
    def test_image(self, client: FlaskClient) -> None:
        start_page = StartPage.open(client)

        assert start_page.metadata.image_url == "http://localhost/static/ate-icons/images/ate-opengraph-image.png"
