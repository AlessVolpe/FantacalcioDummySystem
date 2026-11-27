# SPDX-License-Identifier: AGPL-3.0-only

from collections.abc import Callable
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import SESSION_KEY, logout
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import User

START = "fds_session_started"
SEEN = "fds_session_seen"
GENERATION = "fds_session_generation"


def stamp_session(
    sender: object, request: HttpRequest | None, user: User, **kwargs: object
) -> None:
    if request is None:
        return
    now = timezone.now()
    request.session[START] = int(now.timestamp())
    request.session[SEEN] = int(now.timestamp())
    request.session[GENERATION] = str(user.session_generation)
    request.session.set_expiry(now + timedelta(seconds=settings.FDS_SESSION_ABSOLUTE))


class AccountSessionMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if SESSION_KEY in request.session:
            user = request.user
            started = request.session.get(START)
            seen = request.session.get(SEEN)
            now = int(timezone.now().timestamp())
            if (
                not isinstance(user, User)
                or not isinstance(started, int)
                or not isinstance(seen, int)
                or not started <= seen <= now
                or now - started >= settings.FDS_SESSION_ABSOLUTE
                or now - seen >= settings.FDS_SESSION_IDLE
                or request.session.get(GENERATION) != str(user.session_generation)
            ):
                logout(request)
            elif seen != now:
                request.session[SEEN] = now
        return self.get_response(request)
