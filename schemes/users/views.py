from dataclasses import dataclass

import inject
from flask import Blueprint, Response

from schemes.auth.api_key import api_key_auth
from schemes.users.domain import User
from schemes.users.services import UserRepository

bp = Blueprint("users", __name__)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)


@dataclass
class UserRepr:
    email: str

    def to_domain(self, authority_id: int) -> User:
        return User(email=self.email, authority_id=authority_id)
