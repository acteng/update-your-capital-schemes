from dataclasses import dataclass

import inject
from dataclass_wizard import fromlist
from dataclass_wizard.errors import UnknownJSONKey
from flask import Blueprint, Response, current_app, request

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.users import UserRepr

bp = Blueprint("authorities", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(authorities: AuthorityRepository) -> Response:
    try:
        authorities_repr = fromlist(AuthorityRepr, request.get_json())
    except UnknownJSONKey as error:
        current_app.logger.error(error)
        return Response(status=400)

    authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/users")
@api_key_auth
@inject.autoparams("users")
def add_users(users: UserRepository, authority_id: int) -> Response:
    try:
        users_repr = fromlist(UserRepr, request.get_json())
    except UnknownJSONKey as error:
        current_app.logger.error(error)
        return Response(status=400)

    users.add(*[user_repr.to_domain(authority_id) for user_repr in users_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(authorities: AuthorityRepository) -> Response:
    authorities.clear()
    return Response(status=204)


@dataclass(frozen=True)
class AuthorityRepr:
    id: int
    name: str

    def to_domain(self) -> Authority:
        return Authority(id_=self.id, name=self.name)
