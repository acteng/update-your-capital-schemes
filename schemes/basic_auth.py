import functools
from typing import Callable, ParamSpec, TypeVar

from flask import Response, current_app, request

T = TypeVar("T")
P = ParamSpec("P")


def ui() -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
    return basic_auth("BASIC_AUTH_USERNAME", "BASIC_AUTH_PASSWORD")


def basic_auth(username_config: str, password_config: str) -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T | Response]:
        @functools.wraps(func)
        def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
            return func(*args, **kwargs) if _authorized(username_config, password_config) else _challenge()

        return decorated_function

    return decorator


def _authorized(username_config: str, password_config: str) -> bool:
    username = current_app.config.get(username_config)
    password = current_app.config.get(password_config)

    if username:
        auth = request.authorization
        if not (auth and auth.type == "basic" and auth.username == username and auth.password == password):
            return False

    return True


def _challenge() -> Response:
    return Response(status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response="Unauthorized")
