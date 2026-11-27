# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .problems import MEDIA_TYPE, STATUS_CODES, problem_data


def problem_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        # Let Django handle unexpected exceptions and preserve logging/rollback.
        return None
    status = response.status_code
    code = STATUS_CODES.get(status, "http_error")
    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        code = "authentication_required"
    elif isinstance(exc, exceptions.ValidationError):
        code = "validation_error"
    # Never echo arbitrary serializer keys, raw validation values or exception text.
    response.data = problem_data(code, status)
    response.content_type = MEDIA_TYPE
    response["Cache-Control"] = "no-store"
    return response
