from logging import Logger

import inject
from flask import Blueprint, Response, abort, request
from pydantic import BaseModel, ConfigDict, ValidationError

from schemes.domain.users import User, UserRepository
from schemes.views.auth.api_key import api_key_auth

bp = Blueprint("users", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add_users(users: UserRepository, logger: Logger) -> Response:
    try:
        users_repr = [UserRepr.model_validate(item) for item in request.json]
    except ValidationError as error:
        logger.error(error)
        abort(400)

    users.add(*[user_repr.to_domain() for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)


class UserRepr(BaseModel):
    email: str
    authority_abbreviation: str

    model_config = ConfigDict(extra="forbid")

    def to_domain(self) -> User:
        return User(email=self.email, authority_abbreviation=self.authority_abbreviation)
