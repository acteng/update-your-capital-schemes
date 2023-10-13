from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from urllib.parse import urlencode, urlparse

from authlib.integrations.flask_client import OAuth
from authlib.oidc.core import UserInfo
from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    session,
    url_for,
)
from werkzeug.wrappers import Response as BaseResponse

bp = Blueprint("auth", __name__)


@bp.route("")
def callback() -> BaseResponse:
    oauth = _get_oauth()
    token = oauth.govuk.authorize_access_token()
    user = oauth.govuk.userinfo(token=token)

    if not _is_authorized(user):
        return redirect(url_for("auth.unauthorized"))

    session["user"] = user
    session["id_token"] = token["id_token"]
    return redirect(url_for("home.index"))


@bp.route("/unauthorized")
def unauthorized() -> Response:
    return Response(render_template("unauthorized.html"), status=401)


@bp.route("/logout")
def logout() -> BaseResponse:
    id_token = session["id_token"]
    del session["user"]
    del session["id_token"]

    end_session_endpoint = current_app.config["GOVUK_END_SESSION_ENDPOINT"]
    post_logout_redirect_uri = url_for("start.index", _external=True)
    logout_query = urlencode({"id_token_hint": id_token, "post_logout_redirect_uri": post_logout_redirect_uri})
    logout_url = urlparse(end_session_endpoint)._replace(query=logout_query).geturl()
    return redirect(logout_url)


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


def _is_authorized(user: UserInfo) -> bool:
    users = current_app.extensions["users"]
    return user["email"] in [user.email for user in users]


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]
