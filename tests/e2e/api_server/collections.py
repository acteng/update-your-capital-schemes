from tests.e2e.api_server.base import BaseModel


class CollectionModel[T](BaseModel):
    items: list[T]
