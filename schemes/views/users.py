from dataclasses import dataclass

import inject
from flask import Blueprint, Response

from schemes.domain.users import User, UserRepository
from schemes.views.auth.api_key import api_key_auth

bp = Blueprint("users", __name__)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)


@dataclass(frozen=True)
class UserRepr:
    email: str

    def to_domain(self, authority_id: int) -> User:
        return User(email=self.email, authority_id=authority_id)