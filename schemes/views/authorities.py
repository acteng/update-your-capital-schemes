from logging import Logger

import inject
from flask import Blueprint, Response, abort, request
from pydantic import ValidationError

from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.users import UserRepr

bp = Blueprint("authorities", __name__)


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
