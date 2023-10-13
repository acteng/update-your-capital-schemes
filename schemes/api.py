import inject
from flask import Blueprint, Response, request

from schemes.users import User, UserRepository

bp = Blueprint("api", __name__)


@bp.route("/users", methods=["POST"])
@inject.autoparams()
def add_user(users: UserRepository) -> Response:
    user = User(request.get_json()["email"])
    users.add(user)
    return Response(status=201)


@bp.route("/users", methods=["DELETE"])
@inject.autoparams()
def clear_users(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)
