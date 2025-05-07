from logging import Logger

import inject
from flask import Blueprint, Response, request
from pydantic import BaseModel, ConfigDict, ValidationError

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.users import UserRepr

bp = Blueprint("authorities", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(authorities: AuthorityRepository, logger: Logger) -> Response:
    try:
        authorities_repr = [AuthorityRepr.model_validate(item) for item in request.get_json()]
    except ValidationError as error:
        logger.error(error)
        return Response(status=400)

    authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<authority_abbreviation>/users")
@api_key_auth
@inject.autoparams("users", "logger")
def add_users(users: UserRepository, logger: Logger, authority_abbreviation: str) -> Response:
    try:
        users_repr = [UserRepr.model_validate(item) for item in request.get_json()]
    except ValidationError as error:
        logger.error(error)
        return Response(status=400)

    users.add(*[user_repr.to_domain(authority_abbreviation) for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(authorities: AuthorityRepository) -> Response:
    authorities.clear()
    return Response(status=204)


class AuthorityRepr(BaseModel):
    abbreviation: str
    name: str

    model_config = ConfigDict(extra="forbid")

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, name=self.name)
