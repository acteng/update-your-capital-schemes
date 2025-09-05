from functools import wraps
from typing import Callable

from flask import abort, current_app, request


def api_key_auth[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        api_key = current_app.config.get("API_KEY")
        auth = request.authorization
        if not (auth and auth.type == "api-key" and auth.token == api_key):
            abort(401)
        return func(*args, **kwargs)

    return decorated_function
