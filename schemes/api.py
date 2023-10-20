import inject
from flask import Blueprint, Response, request

from schemes.users import User, UserRepository

bp = Blueprint("api", __name__)


@bp.route("/users", methods=["POST"])
@inject.autoparams()
def add_users(users: UserRepository) -> Response:
    json = request.get_json()
    users.add(*[User(element["email"]) for element in json])
    return Response(status=201)


@bp.route("/users", methods=["DELETE"])
@inject.autoparams()
def clear_users(users: UserRepository) -> Response:
    users.clear()
    return Response(status=204)
