from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, Response, current_app, redirect, session, url_for
from werkzeug.wrappers import Response as BaseResponse

bp = Blueprint("auth", __name__)


@bp.route("")
def callback() -> BaseResponse:
    oauth = _get_oauth()
    token = oauth.govuk.authorize_access_token()
    session["user"] = oauth.govuk.userinfo(token=token)
    session["id_token"] = token["id_token"]
    return redirect(url_for("home.index"))


T = TypeVar("T")
P = ParamSpec("P")


def secure(func: Callable[P, T]) -> Callable[P, T | Response]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        if "user" not in session:
            oauth = _get_oauth()
            callback_url = url_for("auth.callback", _external=True)
            response: Response = oauth.govuk.authorize_redirect(callback_url)
            return response
        return func(*args, **kwargs)

    return decorated_function


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]
