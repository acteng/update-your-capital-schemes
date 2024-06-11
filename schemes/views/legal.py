from flask import Blueprint, render_template

from schemes.views.auth.basic import basic_auth

bp = Blueprint("legal", __name__)


@bp.get("/cookies")
@basic_auth
def cookies() -> str:
    return render_template("legal/cookies.html")
