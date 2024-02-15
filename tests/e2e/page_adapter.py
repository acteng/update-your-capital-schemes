from typing import Literal

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from playwright.sync_api import Page, Response
from werkzeug.test import TestResponse


class FlaskPage(Page):
    def __init__(self, client: FlaskClient):
        super().__init__(FlaskPageImpl(client))


class SyncBaseImpl:
    def __init__(self):
        self._loop = None
        self._dispatcher_fiber = None


class FlaskPageImpl(SyncBaseImpl):
    def __init__(self, client: FlaskClient):
        super().__init__()
        self._client = client
        self._soup = None

    def goto(
        self,
        url: str,
        timeout: float | None = None,
        waitUntil: Literal["commit", "domcontentloaded", "load", "networkidle"] | None = None,
        referer: str | None = None,
    ) -> Response | None:
        response = self._client.get(url)
        self._soup = BeautifulSoup(response.text, "html.parser")
        return FlaskResponse(response)


class FlaskResponse(Response):
    def __init__(self, response: TestResponse):
        super().__init__(FlaskResponseImpl(response))


class FlaskResponseImpl(SyncBaseImpl):
    def __init__(self, response: TestResponse):
        super().__init__()
        self._response = response
