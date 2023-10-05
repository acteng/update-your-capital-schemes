from flask import Blueprint, Response, redirect, render_template, session, url_for
from werkzeug import Response as BaseResponse

bp = Blueprint("start", __name__)


@bp.route("/")
def index() -> BaseResponse:
    if "user" in session:
        return redirect(url_for("home.index"))

    return Response(render_template("start.html"))
