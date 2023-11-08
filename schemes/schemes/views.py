from __future__ import annotations

from dataclasses import asdict, dataclass

import inject
from flask import Blueprint, Response, render_template, session

from schemes.auth.api_key import api_key_auth
from schemes.auth.bearer import bearer_auth
from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.domain import Scheme
from schemes.schemes.services import SchemeRepository
from schemes.users.services import UserRepository

bp = Blueprint("schemes", __name__)


@bp.get("")
@bearer_auth
@inject.autoparams()
def index(users: UserRepository, authorities: AuthorityRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    authority = authorities.get(user.authority_id)
    assert authority
    authority_schemes = schemes.get_by_authority(authority.id)

    context = SchemesContext(authority, authority_schemes)
    return render_template("schemes.html", **asdict(context))


@dataclass
class SchemesContext:
    authority_name: str
    schemes: list[SchemeRowContext]

    def __init__(self, authority: Authority, schemes: list[Scheme]):
        self.authority_name = authority.name
        self.schemes = [SchemeRowContext(scheme) for scheme in schemes]


@dataclass
class SchemeRowContext:
    id: int
    reference: str
    name: str

    def __init__(self, scheme: Scheme):
        self.id = scheme.id
        self.reference = scheme.reference
        self.name = scheme.name


@bp.get("<int:scheme_id>")
@bearer_auth
@inject.autoparams("schemes")
def get(schemes: SchemeRepository, scheme_id: int) -> str:
    scheme = schemes.get(scheme_id)
    assert scheme

    context = SchemeContext(scheme)
    return render_template("scheme.html", **asdict(context))


@dataclass
class SchemeContext:
    name: str
    reference: str

    def __init__(self, scheme: Scheme):
        self.name = scheme.name
        self.reference = scheme.reference


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(schemes: SchemeRepository) -> Response:
    schemes.clear()
    return Response(status=204)


@dataclass
class SchemeRepr:
    id: int
    name: str

    def to_domain(self, authority_id: int) -> Scheme:
        return Scheme(id_=self.id, name=self.name, authority_id=authority_id)
