from flask import Blueprint, Response, redirect, render_template, session, url_for
from werkzeug import Response as BaseResponse

from schemes.auth.basic import basic_auth

bp = Blueprint("start", __name__)


@bp.get("/")
@basic_auth
def index() -> BaseResponse:
    if "user" in session:
        return redirect(url_for("schemes.index"))

    return Response(render_template("start.html"))
