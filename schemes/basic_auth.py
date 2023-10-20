import functools
from typing import Callable, ParamSpec, TypeVar

from flask import Response, current_app, request
from werkzeug.datastructures import Authorization

T = TypeVar("T")
P = ParamSpec("P")
Authorized = Callable[[Authorization | None], bool]


def ui() -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
    def authorized(auth: Authorization | None) -> bool:
        username = current_app.config.get("BASIC_AUTH_USERNAME")
        return not username or _authorized(auth, username, current_app.config["BASIC_AUTH_PASSWORD"])

    return basic_auth(authorized)


def api() -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
    def authorized(auth: Authorization | None) -> bool:
        return _authorized(auth, current_app.config["API_USERNAME"], current_app.config["API_PASSWORD"])

    return basic_auth(authorized)


def basic_auth(authorized: Authorized) -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T | Response]:
        @functools.wraps(func)
        def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
            return func(*args, **kwargs) if authorized(request.authorization) else _challenge()

        return decorated_function

    return decorator


def _authorized(auth: Authorization | None, username: str, password: str) -> bool:
    if not (auth and auth.type == "basic"):
        return False

    return auth.username == username and auth.password == password


def _challenge() -> Response:
    return Response(status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response="Unauthorized")
