from flask import Blueprint, render_template

from schemes.auth import bearer_auth

bp = Blueprint("home", __name__)


@bp.get("")
@bearer_auth
def index() -> str:
    return render_template("home.html")
