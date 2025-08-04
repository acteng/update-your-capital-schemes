from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import Response, abort, current_app, request

T = TypeVar("T")
P = ParamSpec("P")


def api_key_auth(func: Callable[P, T]) -> Callable[P, T | Response]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        api_key = current_app.config.get("API_KEY")
        auth = request.authorization
        if not (auth and auth.type == "api-key" and auth.token == api_key):
            abort(401)
        return func(*args, **kwargs)

    return decorated_function
