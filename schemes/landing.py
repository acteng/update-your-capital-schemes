from flask import Blueprint, render_template

bp = Blueprint("landing", __name__)


@bp.route("/")
def index() -> str:
    return render_template("index.html")
