from typing import Any, Callable

from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc9068 import JWTBearerTokenValidator
from flask import current_app


class TypedResourceProtector(ResourceProtector):  # type: ignore
    def __call__[**P, T](
        self, scopes: str | None = None, optional: bool = False, **kwargs: Any
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        decorator: Callable[[Callable[P, T]], Callable[P, T]] = super().__call__(scopes, optional, **kwargs)
        return decorator


class ApiJwtBearerTokenValidator(JWTBearerTokenValidator):  # type: ignore
    def get_jwks(self) -> Any:
        oauth = current_app.extensions["authlib.integrations.flask_client"]
        return oauth.auth.fetch_jwk_set()


require_oauth = TypedResourceProtector()
