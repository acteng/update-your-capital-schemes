import functools
from typing import Callable, ParamSpec, TypeVar

from flask import Response, current_app, request

T = TypeVar("T")
P = ParamSpec("P")


def basic_auth(func: Callable[P, T]) -> Callable[P, T | Response]:
    @functools.wraps(func)
    def wrapped_view(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        username = current_app.config.get("BASIC_AUTH_USERNAME")
        password = current_app.config.get("BASIC_AUTH_PASSWORD")

        if username:
            auth = request.authorization
            if not (auth and auth.type == "basic" and auth.username == username and auth.password == password):
                return Response(
                    status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response="Unauthorized"
                )

        return func(*args, **kwargs)

    return wrapped_view
