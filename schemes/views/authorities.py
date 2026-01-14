from logging import Logger

import inject
from flask import Blueprint, Response, abort, request
from pydantic import BaseModel, ConfigDict, ValidationError

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth, async_api_key_auth
from schemes.views.users import UserRepr

bp = Blueprint("authorities", __name__)


@bp.post("")
@async_api_key_auth
@inject.autoparams()
async def add(authorities: AuthorityRepository, logger: Logger) -> Response:
    try:
        authorities_repr = [AuthorityRepr.model_validate(item) for item in request.json]
    except ValidationError as error:
        logger.error(error)
        abort(400)

    await authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<authority_abbreviation>/users")
@api_key_auth
@inject.autoparams("users", "logger")
def add_users(users: UserRepository, logger: Logger, authority_abbreviation: str) -> Response:
    try:
        users_repr = [UserRepr.model_validate(item) for item in request.json]
    except ValidationError as error:
        logger.error(error)
        abort(400)

    users.add(*[user_repr.to_domain(authority_abbreviation) for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@async_api_key_auth
@inject.autoparams()
async def clear(authorities: AuthorityRepository) -> Response:
    await authorities.clear()
    return Response(status=204)


class AuthorityRepr(BaseModel):
    abbreviation: str
    name: str

    model_config = ConfigDict(extra="forbid")

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, name=self.name)
