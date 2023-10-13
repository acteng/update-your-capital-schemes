from flask import Blueprint, Response, current_app, request

from schemes.users import User, UserRepository

bp = Blueprint("api", __name__)


@bp.route("/users", methods=["POST"])
def add_user() -> Response:
    user = User(request.get_json()["email"])
    users: UserRepository = current_app.extensions["users"]
    users.add(user)
    return Response(status=201)


@bp.route("/users", methods=["DELETE"])
def clear_users() -> Response:
    users: UserRepository = current_app.extensions["users"]
    users.clear()
    return Response(status=204)
