from functools import wraps
from typing import Callable

from authlib.jose import jwt
from flask import current_app, request


def jwt_bearer_auth[T, **P](func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        _validate_jwt()
        return func(*args, **kwargs)

    return decorated_function


def _validate_jwt() -> None:
    assert request.authorization

    oauth = current_app.extensions["authlib.integrations.flask_client"]
    server_metadata = oauth.auth.load_server_metadata()
    jwks = oauth.auth.fetch_jwk_set()

    claims = jwt.decode(
        request.authorization.token,
        key=jwks,
        claims_options={
            "iss": {"value": server_metadata.get("issuer")},
            "aud": {"value": current_app.config["RESOURCE_SERVER_IDENTIFIER"]},
        },
    )
    claims.validate()
