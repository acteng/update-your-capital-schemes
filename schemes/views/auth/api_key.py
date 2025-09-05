from functools import wraps
from typing import Awaitable, Callable

from flask import abort, current_app, request


def api_key_auth[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        _check_api_key()
        return func(*args, **kwargs)

    return decorated_function


def async_api_key_auth[**P, T](func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        _check_api_key()
        return await func(*args, **kwargs)

    return decorated_function


def _check_api_key() -> None:
    api_key = current_app.config.get("API_KEY")
    auth = request.authorization
    if not (auth and auth.type == "api-key" and auth.token == api_key):
        abort(401)
