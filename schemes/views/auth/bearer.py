from functools import wraps
from logging import Logger
from typing import Awaitable, Callable
from urllib.parse import urlencode, urljoin

import inject
from authlib.integrations.flask_client import OAuth
from authlib.oidc.core import UserInfo
from flask import Blueprint, Request, Response, abort, current_app, redirect, render_template, request, session, url_for
from werkzeug.wrappers import Response as BaseResponse

from schemes.domain.users import UserRepository

bp = Blueprint("auth", __name__)


@bp.get("")
@inject.autoparams()
def callback(users: UserRepository, logger: Logger) -> BaseResponse:
    if "user" not in session:
        if not _is_authorization_response(request) and not _is_error_response(request):
            abort(400)

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
            logger.warning("User '%s' unauthorized sign in attempt", user.email)
            return redirect(url_for("auth.forbidden"))

        session["user"] = user
        session["id_token"] = token["id_token"]

        logger.info("User '%s' successfully signed in", user.email)

    return redirect(url_for("schemes.index"))


@bp.get("/forbidden")
def forbidden() -> Response:
    return Response(render_template("403.html"), status=403)


@bp.get("/logout")
@inject.autoparams()
def logout(logger: Logger) -> BaseResponse:
    id_token = session.pop("id_token", None)
    user = session.pop("user", None)

    if user:
        logger.info("User '%s' signed out", user["email"])
    else:
        logger.info("User signed out")

    end_session_endpoint = current_app.config["GOVUK_END_SESSION_ENDPOINT"]

    if id_token:
        post_logout_redirect_uri = url_for("start.index", _external=True)
        logout_query = urlencode({"id_token_hint": id_token, "post_logout_redirect_uri": post_logout_redirect_uri})
        end_session_endpoint = urljoin(end_session_endpoint, "?" + logout_query)

    return redirect(end_session_endpoint)


def bearer_auth[**P, T](func: Callable[P, T]) -> Callable[P, T | Response]:
    @wraps(func)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        response = _check_bearer()
        return response if response else func(*args, **kwargs)

    return decorated_function


def async_bearer_auth[**P, T](func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | Response]]:
    @wraps(func)
    async def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | Response:
        response = _check_bearer()
        return response if response else await func(*args, **kwargs)

    return decorated_function


def _is_authorization_response(request: Request) -> bool:
    # See: https://www.rfc-editor.org/rfc/rfc6749#section-4.1.2
    return "code" in request.args and "state" in request.args


def _is_error_response(request: Request) -> bool:
    # See: https://www.rfc-editor.org/rfc/rfc6749#section-4.1.2.1
    return "error" in request.args


def _is_authorized(users: UserRepository, user: UserInfo) -> bool:
    return users.get(user["email"]) is not None


def _get_oauth() -> OAuth:
    return current_app.extensions["authlib.integrations.flask_client"]


def _check_bearer() -> Response | None:
    if "user" not in session:
        oauth = _get_oauth()
        callback_url = url_for("auth.callback", _external=True)
        response: Response = oauth.govuk.authorize_redirect(callback_url)
        return response

    return None
