from functools import wraps
from typing import Callable, ParamSpec, TypeVar
from urllib.parse import urlencode, urlparse

import inject
from authlib.integrations.flask_client import OAuth
from authlib.oidc.core import UserInfo
from flask import Blueprint, Response, abort, current_app, redirect, session, url_for
from werkzeug.wrappers import Response as BaseResponse

from schemes.domain.users import UserRepository

bp = Blueprint("auth", __name__)


@bp.get("")
@inject.autoparams()
def callback(users: UserRepository) -> BaseResponse:
    oauth = _get_oauth()
    server_metadata = oauth.govuk.load_server_metadata()
    token = oauth.govuk.authorize_access_token(
        claims_options={
            "iss": {"value": server_metadata.get("issuer")},
            "aud": {"value": oauth.govuk.client_id},
        }
    )
    user = oauth.govuk.userinfo(token=token)

    if not _is_authorized(users, user):
        abort(403)

    session["user"] = user
    session["id_token"] = token["id_token"]
    return redirect(url_for("schemes.index"))


@bp.get("/logout")
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


def bearer_auth(func: Callable[P, T]) -> Callable[P, T | Response]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        if "user" not in session:
            oauth = _get_oauth()
            callback_url = url_for("auth.callback", _external=True)
            response: Response = oauth.govuk.authorize_redirect(callback_url)
            return response
        return func(*args, **kwargs)

    return decorated_function


def _is_authorized(users: UserRepository, user: UserInfo) -> bool:
    return users.get_by_email(user["email"]) is not None


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]
