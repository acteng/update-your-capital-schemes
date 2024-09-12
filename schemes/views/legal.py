from flask import Blueprint, Response, render_template, send_from_directory

from schemes.views.auth.basic import basic_auth

bp = Blueprint("legal", __name__)


@bp.get("/privacy")
@basic_auth
def privacy() -> str:
    return render_template("legal/privacy.html")


@bp.get("/accessibility")
@basic_auth
def accessibility() -> str:
    return render_template("legal/accessibility.html")


@bp.get("/cookies")
@basic_auth
def cookies() -> str:
    return render_template("legal/cookies.html")


@bp.get("/.well-known/security.txt")
def security() -> Response:
    return send_from_directory(directory="views/templates/legal", path="security.txt")
