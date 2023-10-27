import inject
from flask import Blueprint, render_template, session

from schemes.auth import bearer_auth
from schemes.authorities import AuthorityRepository
from schemes.users import UserRepository

bp = Blueprint("schemes", __name__)


@bp.get("")
@bearer_auth
@inject.autoparams()
def index(users: UserRepository, authorities: AuthorityRepository) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    authority = authorities.get(user.authority_id)
    assert authority

    return render_template("schemes.html", authority_name=authority.name)
