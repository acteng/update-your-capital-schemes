from dataclasses import dataclass

import inject
from dataclass_wizard import fromlist
from flask import Blueprint, Response, request

from schemes.auth.api_key import api_key_auth
from schemes.domain.authorities import Authority
from schemes.services.authorities import AuthorityRepository
from schemes.services.schemes import SchemeRepository
from schemes.services.users import UserRepository
from schemes.views.schemes import SchemeRepr
from schemes.views.users import UserRepr

bp = Blueprint("authorities", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(authorities: AuthorityRepository) -> Response:
    authorities_repr = fromlist(AuthorityRepr, request.get_json())
    authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/users")
@api_key_auth
@inject.autoparams("users")
def add_users(users: UserRepository, authority_id: int) -> Response:
    users_repr = fromlist(UserRepr, request.get_json())
    users.add(*[user_repr.to_domain(authority_id) for user_repr in users_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/schemes")
@api_key_auth
@inject.autoparams("schemes")
def add_schemes(schemes: SchemeRepository, authority_id: int) -> Response:
    schemes_repr = fromlist(SchemeRepr, request.get_json())
    schemes.add(*[scheme_repr.to_domain(authority_id) for scheme_repr in schemes_repr])
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
