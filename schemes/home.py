from flask import Blueprint, render_template

from schemes.auth import secure

bp = Blueprint("home", __name__)


@bp.get("")
@secure
def index() -> str:
    return render_template("home.html")
