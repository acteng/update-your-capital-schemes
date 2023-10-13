from flask import Blueprint, Response, current_app, request

from schemes.users import User

bp = Blueprint("api", __name__)


@bp.route("/users", methods=["POST"])
def add_user() -> Response:
    user = User(request.get_json()["email"])
    current_app.extensions["users"].append(user)
    return Response(status=201)


@bp.route("/users", methods=["DELETE"])
def clear_users() -> Response:
    current_app.extensions["users"].clear()
    return Response(status=204)
