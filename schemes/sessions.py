from flask import Flask, Request, Response
from flask.sessions import SessionInterface, SessionMixin


class DelegatingSessionInterface(SessionInterface):
    def __init__(self, delegate: SessionInterface):
        self._delegate = delegate

    def open_session(self, app: Flask, request: Request) -> SessionMixin | None:
        return self._delegate.open_session(app, request)

    def save_session(self, app: Flask, session: SessionMixin, response: Response) -> None:
        return self._delegate.save_session(app, session, response)


class RequestFilteringSessionInterface(DelegatingSessionInterface):
    def __init__(self, delegate: SessionInterface, exclude_path_prefix: str):
        super().__init__(delegate)
        self._exclude_path_prefix = exclude_path_prefix

    def open_session(self, app: Flask, request: Request) -> SessionMixin | None:
        if request.path.startswith(self._exclude_path_prefix):
            return self.make_null_session(app)

        return super().open_session(app, request)
