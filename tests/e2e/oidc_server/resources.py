from typing import Any, Callable

from authlib.integrations.flask_oauth2 import ResourceProtector


class TypedResourceProtector(ResourceProtector):  # type: ignore
    def __call__[**P, T](
        self, scopes: str | None = None, optional: bool = False, **kwargs: Any
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        decorator: Callable[[Callable[P, T]], Callable[P, T]] = super().__call__(scopes, optional, **kwargs)
        return decorator
