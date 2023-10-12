from flask import Blueprint, Response, current_app, request

bp = Blueprint("api", __name__)


@bp.route("/users", methods=["POST"])
def add_user() -> Response:
    email = request.get_json()["email"]
    current_app.extensions["users"].append(email)
    return Response(status=201)


@bp.route("/users", methods=["DELETE"])
def clear_users() -> Response:
    current_app.extensions["users"].clear()
    return Response(status=204)
