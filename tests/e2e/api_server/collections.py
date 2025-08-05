from schemes.infrastructure.api.base import BaseModel


class CollectionModel[T](BaseModel):
    items: list[T]
