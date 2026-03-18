from functools import wraps
from typing import Callable

from flask import Response, current_app, request


def basic_auth[**P, T](func: Callable[P, T]) -> Callable[P, T | Response]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        username = current_app.config.get("BASIC_AUTH_USERNAME")
        password = current_app.config.get("BASIC_AUTH_PASSWORD")
        auth = request.authorization

        if username:
            if not (auth and auth.type == "basic"):
                return _create_unauthorized_response("Not authenticated")

            if not (auth.username == username and auth.password == password):
                return _create_unauthorized_response("Unauthorized")

        return func(*args, **kwargs)

    return decorated_function


def _create_unauthorized_response(text: str) -> Response:
    return Response(status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response=text)
