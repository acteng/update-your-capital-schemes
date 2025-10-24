from functools import wraps
from typing import Any, Callable

from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc9068 import JWTBearerTokenValidator
from flask import current_app


class ApiJwtBearerTokenValidator(JWTBearerTokenValidator):  # type: ignore
    def get_jwks(self) -> Any:
        return _get_oauth().auth.fetch_jwk_set()


def require_oauth[T, **P](func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        server_metadata = _get_oauth().auth.load_server_metadata()
        issuer = server_metadata.get("issuer")
        resource_server_identifier = current_app.config["RESOURCE_SERVER_IDENTIFIER"]

        resource_protector = ResourceProtector()
        resource_protector.register_token_validator(ApiJwtBearerTokenValidator(issuer, resource_server_identifier))
        response: T = resource_protector()(func)(*args, **kwargs)
        return response

    return decorated_function


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]
