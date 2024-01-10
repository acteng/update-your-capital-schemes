from datetime import datetime

import inject
from flask import Blueprint, Response, request

from schemes.infrastructure.clock import Clock
from schemes.views.auth.api_key import api_key_auth

bp = Blueprint("clock", __name__)


@bp.put("")
@api_key_auth
@inject.autoparams()
def set_clock(clock: Clock) -> Response:
    now = datetime.fromisoformat(request.form["now"])
    clock.now = now
    return Response(status=204)
