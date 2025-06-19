from typing import Any, Iterator
from unittest.mock import patch

import pytest
from flask import Flask, Response, request
from flask.sessions import NullSession, SessionInterface, SessionMixin

from schemes.sessions import DelegatingSessionInterface, RequestFilteringSessionInterface


@pytest.fixture(name="app")
def app_fixture() -> Flask:
    return Flask("test")


class TestDelegatingSessionInterface:
    def test_open_session_delegates(self, app: Flask) -> None:
        delegate = DummySessionInterface()
        delegating = DelegatingSessionInterface(delegate)
        session = NullSession()

        with patch.object(delegate, "open_session", return_value=session) as open_session:
            actual_session = delegating.open_session(app, request)

            open_session.assert_called_once_with(app, request)
            assert actual_session == session

    def test_save_session_delegates(self, app: Flask) -> None:
        delegate = DummySessionInterface()
        delegating = DelegatingSessionInterface(delegate)
        session = NullSession()
        response = Response()

        with patch.object(delegate, "save_session") as save_session:
            delegating.save_session(app, session, response)

            save_session.assert_called_once_with(app, session, response)


class TestRequestFilteringSessionInterface:
    def test_open_session_filters_matched_request(self, app: Flask) -> None:
        delegate = DummySessionInterface()
        filtering = RequestFilteringSessionInterface(delegate, "/static/")

        with app.test_request_context(path="/static/main.css"):
            actual_session = filtering.open_session(app, request)

            assert isinstance(actual_session, NullSession)

    def test_open_session_delegates_unmatched_request(self, app: Flask) -> None:
        delegate = DummySessionInterface()
        filtering = RequestFilteringSessionInterface(delegate, "/static/")
        session = DummySession()

        with patch.object(delegate, "open_session", return_value=session), app.test_request_context(path="/home"):
            actual_session = filtering.open_session(app, request)

            assert actual_session is session


class DummySessionInterface(SessionInterface):
    pass


class DummySession(SessionMixin):
    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError()

    def __getitem__(self, key: str) -> Any:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError()
