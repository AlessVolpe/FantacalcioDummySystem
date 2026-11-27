# SPDX-License-Identifier: AGPL-3.0-only

"""Explicit OpenAPI descriptions for the preserved Django auth endpoints.

The hook runs on the DRF-generated document, leaving future DRF resources
untouched. Initial operations are explicit because Django views are not
introspectable by drf-spectacular and their error bodies are not DRF defaults.
"""

from typing import Any

from ..problems import MEDIA_TYPE

type Schema = dict[str, Any]

STRING: Schema = {"type": "string"}
EMAIL: Schema = {"type": "string", "format": "email", "maxLength": 254}
PASSWORD: Schema = {
    "type": "string",
    "minLength": 12,
    "maxLength": 128,
    "writeOnly": True,
}
CURRENT_PASSWORD: Schema = {**PASSWORD, "minLength": 1}
TOKEN: Schema = {"type": "string", "pattern": "^[A-Za-z0-9_-]{43}$", "writeOnly": True}
NAME: Schema = {"type": "string", "minLength": 1, "maxLength": 150}


def obj(**properties: Schema) -> Schema:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def body(schema: Schema, media_type: str = "application/json") -> Schema:
    return {media_type: {"schema": schema}}


def ref(name: str) -> Schema:
    return {"$ref": f"#/components/schemas/{name}"}


def operation(
    name: str,
    summary: str,
    status: int,
    *,
    request: Schema | None = None,
    response: Schema | None = None,
    errors: tuple[int, ...] = (),
    protected: bool = False,
    unsafe: bool = False,
    tag: str = "Authentication",
) -> Schema:
    success: Schema = {"description": "Successful response"}
    if response is not None:
        success["content"] = body(response)
    responses = {str(status): success}
    for error_status in (*errors, 500):
        responses[str(error_status)] = {
            "description": "Problem Details response",
            "content": body(ref("Problem"), MEDIA_TYPE),
        }
    security: dict[str, list[str]] = {}
    if protected:
        security["cookieAuth"] = []
    if unsafe:
        security["csrfToken"] = []
    result: Schema = {
        "operationId": name,
        "summary": summary,
        "tags": [tag],
        "security": [security] if security else [],
        "responses": responses,
    }
    if request is not None:
        result["requestBody"] = {"required": True, "content": body(request)}
    return result


def add_initial_contract(
    result: Schema, generator: object, request: object, public: bool
) -> Schema:
    components = result.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas["Problem"] = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "format": "uri-reference"},
            "title": STRING,
            "status": {"type": "integer", "minimum": 400, "maximum": 599},
            "detail": STRING,
            "code": STRING,
        },
        "required": ["type", "title", "status", "detail", "code"],
    }
    schemas["OwnIdentity"] = obj(
        id={"type": "string", "format": "uuid", "readOnly": True},
        email={**EMAIL, "readOnly": True},
        display_name=NAME,
    )
    components.setdefault("securitySchemes", {})["cookieAuth"] = {
        "type": "apiKey",
        "in": "cookie",
        "name": "sessionid",
    }
    components["securitySchemes"]["csrfToken"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-CSRFToken",
        "description": (
            "CSRF protection, not an authentication credential. Obtain a token "
            "from GET /api/v1/auth/csrf/ and retain its cookie. Refresh after login. "
            "Swagger UI supplies it automatically."
        ),
    }
    paths = result.setdefault("paths", {})
    base = "/api/v1/auth/"
    accepted = obj(status={"type": "string", "const": "accepted"})
    paths[base + "csrf/"] = {
        "get": operation(
            "authCsrf",
            "Obtain a CSRF token",
            200,
            response=obj(csrfToken=STRING),
            errors=(405,),
        )
    }
    for route, name, summary in (
        ("register/", "authRegister", "Request a registration email"),
        ("resend/", "authResend", "Resend a registration email"),
        ("password/reset/", "authResetRequest", "Request password recovery"),
    ):
        paths[base + route] = {
            "post": operation(
                name,
                summary,
                202,
                request=obj(email=EMAIL),
                response=accepted,
                errors=(400, 403, 405, 429, 503),
                unsafe=True,
            )
        }
    errors: tuple[int, ...]
    for route, name, summary, status, fields, errors, protected in (
        (
            "verify/",
            "authVerify",
            "Complete email-first registration",
            201,
            obj(token=TOKEN, display_name=NAME, password=PASSWORD),
            (400, 403, 405, 429, 503),
            False,
        ),
        (
            "login/",
            "authLogin",
            "Establish a session",
            204,
            obj(email=EMAIL, password=CURRENT_PASSWORD),
            (400, 403, 405, 429),
            False,
        ),
        (
            "logout/",
            "authLogout",
            "Terminate the current session",
            204,
            None,
            (403, 405),
            False,
        ),
        (
            "password/confirm/",
            "authResetConfirm",
            "Complete password recovery",
            204,
            obj(token=TOKEN, password=PASSWORD),
            (400, 403, 405, 429, 503),
            False,
        ),
        (
            "password/change/",
            "authPasswordChange",
            "Change the authenticated password",
            204,
            obj(current_password=CURRENT_PASSWORD, password=PASSWORD),
            (400, 403, 405, 429),
            True,
        ),
    ):
        paths[base + route] = {
            "post": operation(
                name,
                summary,
                status,
                request=fields,
                errors=errors,
                protected=protected,
                unsafe=True,
            )
        }
    paths[base + "me/"] = {
        "get": operation(
            "authMe",
            "Read the current account",
            200,
            response=ref("OwnIdentity"),
            errors=(403, 405),
            protected=True,
        ),
        "patch": operation(
            "authUpdateMe",
            "Change the current display name",
            200,
            request=obj(display_name=NAME),
            response=ref("OwnIdentity"),
            errors=(400, 403, 405, 406, 413, 415),
            protected=True,
            unsafe=True,
        ),
    }
    for route, name, summary, errors in (
        ("live/", "healthLive", "Application liveness", (405, 406)),
        ("ready/", "healthReady", "PostgreSQL readiness", (405, 406, 503)),
    ):
        paths["/api/v1/health/" + route] = {
            "get": operation(
                name,
                summary,
                200,
                response=obj(status={"type": "string", "const": "ok"}),
                errors=errors,
                tag="Health",
            )
        }
    result["paths"] = dict(sorted(paths.items()))
    return result
