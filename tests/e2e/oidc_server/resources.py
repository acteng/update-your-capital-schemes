from typing import Callable

from authlib.integrations.flask_oauth2 import ResourceProtector
from flask import Response


class TypedResourceProtector(ResourceProtector):  # type: ignore
    def __call__[**P, T](
        self, scopes: str | None = None, optional: bool = False
    ) -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
        decorator: Callable[[Callable[P, T]], Callable[P, T | Response]] = super().__call__(scopes, optional)
        return decorator
