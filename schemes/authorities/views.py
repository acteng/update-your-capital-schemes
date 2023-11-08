from dataclasses import dataclass

import inject
from flask import Blueprint, Response, request

from schemes.auth.api_key import api_key_auth
from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.services import SchemeRepository
from schemes.schemes.views import SchemeRepr
from schemes.users.services import UserRepository
from schemes.users.views import UserRepr

bp = Blueprint("authorities", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams()
def add(authorities: AuthorityRepository) -> Response:
    authorities_repr = [AuthorityRepr(**element) for element in request.get_json()]
    authorities.add(*[authority_repr.to_domain() for authority_repr in authorities_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/users")
@api_key_auth
@inject.autoparams("users")
def add_users(users: UserRepository, authority_id: int) -> Response:
    users_repr = [UserRepr(**element) for element in request.get_json()]
    users.add(*[user_repr.to_domain(authority_id) for user_repr in users_repr])
    return Response(status=201)


@bp.post("<int:authority_id>/schemes")
@api_key_auth
@inject.autoparams("schemes")
def add_schemes(schemes: SchemeRepository, authority_id: int) -> Response:
    schemes_repr = [SchemeRepr(**element) for element in request.get_json()]
    schemes.add(*[scheme_repr.to_domain(authority_id) for scheme_repr in schemes_repr])
    return Response(status=201)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(authorities: AuthorityRepository) -> Response:
    authorities.clear()
    return Response(status=204)


@dataclass
class AuthorityRepr:
    id: int
    name: str

    def to_domain(self) -> Authority:
        return Authority(id_=self.id, name=self.name)
