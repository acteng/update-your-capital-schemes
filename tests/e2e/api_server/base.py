from pydantic import BaseModel as pydantic_BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(pydantic_BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
