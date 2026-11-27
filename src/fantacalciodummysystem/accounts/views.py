# SPDX-License-Identifier: AGPL-3.0-only

import json
import re
from collections.abc import Callable
from functools import wraps
from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.exceptions import RequestDataTooBig, ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.csrf import csrf_failure as default_csrf_failure

from fantacalciodummysystem.api.parsers import reject_constant, unique_object
from fantacalciodummysystem.api.problems import is_api, problem

from . import lifecycle
from .managers import canonical_email, validate_identity_email
from .models import User
from .throttles import login_budget, mail_budget, token_budget

type View = Callable[[HttpRequest], HttpResponse]


def error(code: str, status: int) -> JsonResponse:
    return problem(code, status)


def accepted() -> JsonResponse:
    return JsonResponse({"status": "accepted"}, status=202)


def endpoint(method: str) -> Callable[[View], View]:
    def decorate(view: View) -> View:
        @wraps(view)
        def wrapped(request: HttpRequest) -> HttpResponse:
            response: HttpResponse
            if request.method != method:
                response = error("method_not_allowed", 405)
                response["Allow"] = method
            else:
                try:
                    response = view(request)
                except (ValidationError, ValueError, RequestDataTooBig, RecursionError):
                    response = error("invalid_input", 400)
            response["Cache-Control"] = "no-store"
            response["Referrer-Policy"] = "no-referrer"
            return response

        return wrapped

    return decorate


def csrf_failure(request: HttpRequest, reason: str = "") -> HttpResponse:
    if is_api(request):
        response = error("csrf_failed", 403)
        response["Cache-Control"] = "no-store"
        return response
    return default_csrf_failure(request, reason=reason)


def payload(request: HttpRequest, *fields: str) -> dict[str, str]:
    if request.content_type != "application/json" or len(request.body) > 16384:
        raise ValueError("Invalid request body")
    data = json.loads(
        request.body.decode("utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )
    if not isinstance(data, dict) or set(data) != set(fields):
        raise ValueError("Invalid request fields")
    result: dict[str, str] = {}
    for name in fields:
        value = data[name]
        if not isinstance(value, str) or "\x00" in value:
            raise ValueError("Invalid field")
        value.encode("utf-8")  # Reject isolated Unicode surrogates.
        result[name] = value
    return result


def email_value(value: str) -> str:
    email = canonical_email(value)
    validate_identity_email(email)
    return email


def token_value(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{43}", value) is None:
        raise ValueError("Invalid token")
    return value


def password_value(value: str) -> str:
    if not 1 <= len(value) <= 128:
        raise ValueError("Invalid password length")
    return value


def mail_request(request: HttpRequest, purpose: str) -> HttpResponse:
    if not settings.FDS_AUTH_EMAIL_ENABLED:
        return error("email_flow_unavailable", 503)
    email = email_value(payload(request, "email")["email"])
    ip_allowed, email_allowed = mail_budget(purpose, request, email)
    if not ip_allowed:
        return error("rate_limited", 429)
    if email_allowed:
        lifecycle.issue(email, purpose)
    return accepted()


@endpoint("GET")
def csrf(request: HttpRequest) -> HttpResponse:
    return JsonResponse({"csrfToken": get_token(request)})


@endpoint("POST")
def register(request: HttpRequest) -> HttpResponse:
    return mail_request(request, lifecycle.REGISTER)


@endpoint("POST")
def resend(request: HttpRequest) -> HttpResponse:
    return mail_request(request, lifecycle.REGISTER)


@endpoint("POST")
def verify(request: HttpRequest) -> HttpResponse:
    if not settings.FDS_AUTH_EMAIL_ENABLED:
        return error("email_flow_unavailable", 503)
    if not token_budget(request):
        return error("rate_limited", 429)
    data = payload(request, "token", "display_name", "password")
    name = data["display_name"].strip()
    if not 1 <= len(name) <= 150:
        raise ValueError("Invalid display name")
    if not lifecycle.register(
        token_value(data["token"]), name, password_value(data["password"])
    ):
        return error("invalid_token", 400)
    return HttpResponse(status=201)


@endpoint("POST")
def sign_in(request: HttpRequest) -> HttpResponse:
    data = payload(request, "email", "password")
    email = email_value(data["email"])
    password = password_value(data["password"])
    with login_budget(request, email) as budget:
        if not budget.allowed:
            return error("rate_limited", 429)
        user = authenticate(request, email=email, password=password)
        if not isinstance(user, User):
            return error("invalid_credentials", 403)
        # Always discard any prior session, including reauthentication as the
        # same user, before Django establishes the new authenticated session.
        request.session.flush()
        login(request, user)
        budget.succeeded = True
    return HttpResponse(status=204)


@endpoint("POST")
def sign_out(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse(status=204)


@endpoint("POST")
def reset_request(request: HttpRequest) -> HttpResponse:
    return mail_request(request, lifecycle.RESET)


@endpoint("POST")
def reset_confirm(request: HttpRequest) -> HttpResponse:
    if not settings.FDS_AUTH_EMAIL_ENABLED:
        return error("email_flow_unavailable", 503)
    if not token_budget(request):
        return error("rate_limited", 429)
    data = payload(request, "token", "password")
    if not lifecycle.reset(
        token_value(data["token"]), password_value(data["password"])
    ):
        return error("invalid_token", 400)
    return HttpResponse(status=204)


@endpoint("POST")
def password_change(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not isinstance(user, User):
        return error("authentication_required", 403)
    data = payload(request, "current_password", "password")
    current = password_value(data["current_password"])
    password = password_value(data["password"])
    with login_budget(request, user.email) as budget:
        if not budget.allowed:
            return error("rate_limited", 429)
        try:
            fresh = lifecycle.change_password(user, current, password)
        except lifecycle.InvalidCredentials:
            return error("invalid_credentials", 403)
        except ValidationError:
            budget.succeeded = True
            return error("invalid_input", 400)
        update_session_auth_hash(request, fresh)
        budget.succeeded = True
    return HttpResponse(status=204)


@endpoint("GET")
def me(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not isinstance(user, User):
        return error("authentication_required", 403)
    return JsonResponse(
        {"id": str(user.pk), "email": user.email, "display_name": user.display_name}
    )


def completion_page(request: HttpRequest, *, registration: bool) -> HttpResponse:
    if not settings.FDS_AUTH_EMAIL_ENABLED:
        return error("email_flow_unavailable", 503)
    nonce = token_urlsafe(24)
    response = render(
        request,
        "accounts/complete.html",
        {
            "registration": registration,
            "nonce": nonce,
            "endpoint": (
                "/api/v1/auth/verify/"
                if registration
                else "/api/v1/auth/password/confirm/"
            ),
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
        f"script-src 'nonce-{nonce}'; connect-src 'self'; form-action 'self'"
    )
    return response


@endpoint("GET")
def registration_page(request: HttpRequest) -> HttpResponse:
    return completion_page(request, registration=True)


@endpoint("GET")
def reset_page(request: HttpRequest) -> HttpResponse:
    return completion_page(request, registration=False)
