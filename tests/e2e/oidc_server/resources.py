from typing import Callable, ParamSpec, TypeVar

from authlib.integrations.flask_oauth2 import ResourceProtector
from flask import Response

T = TypeVar("T")
P = ParamSpec("P")


class TypedResourceProtector(ResourceProtector):  # type: ignore
    def __call__(
        self, scopes: str | None = None, optional: bool = False
    ) -> Callable[[Callable[P, T]], Callable[P, T | Response]]:
        decorator: Callable[[Callable[P, T]], Callable[P, T | Response]] = super().__call__(scopes, optional)
        return decorator
