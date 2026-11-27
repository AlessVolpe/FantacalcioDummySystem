# SPDX-License-Identifier: AGPL-3.0-only

"""Shared RFC 9457 responses without exception or request-data disclosure."""

from collections.abc import Callable
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse

MEDIA_TYPE = "application/problem+json"
STATUS_CODES = {
    400: "invalid_input",
    401: "authentication_required",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    409: "conflict",
    413: "payload_too_large",
    415: "unsupported_media_type",
    429: "rate_limited",
    500: "internal_error",
    503: "service_unavailable",
}
DETAILS = {
    "invalid_input": "The submitted request is invalid.",
    "validation_error": "The submitted data is invalid.",
    "invalid_credentials": "The supplied credentials were not accepted.",
    "invalid_token": "The token is invalid or no longer usable.",
    "authentication_required": "Authentication is required.",
    "csrf_failed": "CSRF verification failed.",
    "permission_denied": "The requested operation is not permitted.",
    "not_found": "The requested resource was not found.",
    "method_not_allowed": "The HTTP method is not supported here.",
    "not_acceptable": "The requested response representation is not supported.",
    "conflict": "The request conflicts with the current resource state.",
    "payload_too_large": "The request body exceeds the permitted size.",
    "unsupported_media_type": "The request media type is not supported.",
    "rate_limited": "Too many requests. Try again later.",
    "internal_error": "An unexpected internal error occurred.",
    "service_unavailable": "The service is temporarily unavailable.",
    "email_flow_unavailable": "This email-based operation is unavailable.",
}


def problem_data(code: str, status: int) -> dict[str, str | int]:
    # about:blank uses the standard HTTP status phrase; code is an extension.
    try:
        title = HTTPStatus(status).phrase
    except ValueError:
        title = "HTTP error"
    return {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": DETAILS.get(code, "The request could not be completed."),
        "code": code,
    }


def problem(code: str, status: int) -> JsonResponse:
    response = JsonResponse(
        problem_data(code, status), status=status, content_type=MEDIA_TYPE
    )
    response["Cache-Control"] = "no-store"
    return response


def is_api(request: HttpRequest) -> bool:
    return request.path_info == "/api/v1" or request.path_info.startswith("/api/v1/")


class ApiResponseMiddleware:
    """Cover Django-level failures as well as DRF's handled exceptions."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if not is_api(request):
            return response
        status = response.status_code
        media_type = response.get("Content-Type", "").partition(";")[0]
        if status >= 400 and media_type != MEDIA_TYPE:
            replacement = problem(STATUS_CODES.get(status, "http_error"), status)
            for header in ("Allow", "Retry-After", "WWW-Authenticate", "Vary"):
                if header in response:
                    replacement[header] = response[header]
            replacement.cookies = response.cookies
            response = replacement
        response["Cache-Control"] = "no-store"
        response["Referrer-Policy"] = "no-referrer"
        return response
