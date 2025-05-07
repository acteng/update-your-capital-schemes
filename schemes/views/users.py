import inject
from flask import Blueprint, Response
from pydantic import BaseModel, ConfigDict

from schemes.domain.users import User, UserRepository
from schemes.views.auth.api_key import api_key_auth

bp = Blueprint("users", __name__)


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)


class UserRepr(BaseModel):
    email: str

    model_config = ConfigDict(extra="forbid")

    def to_domain(self, authority_abbreviation: str) -> User:
        return User(email=self.email, authority_abbreviation=authority_abbreviation)
