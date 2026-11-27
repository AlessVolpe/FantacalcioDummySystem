# SPDX-License-Identifier: AGPL-3.0-only

import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import persistent_secret, postgres, production_hosts, required

DEBUG = False
SECRET_KEY = persistent_secret("FDS_SECRET_KEY")
ALLOWED_HOSTS = production_hosts()
DATABASES = postgres("FDS_DB_")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Configure trusted proxy headers only when the reverse proxy is deployed.
# Keep email-based flows disabled until delivery and frontend are operational.
FDS_AUTH_EMAIL_ENABLED = os.environ.get("FDS_AUTH_EMAIL_ENABLED") == "1"
if FDS_AUTH_EMAIL_ENABLED:
    FDS_AUTH_ORIGIN = required("FDS_AUTH_ORIGIN")
    try:
        origin = urlsplit(FDS_AUTH_ORIGIN)
        valid_origin = (
            origin.scheme == "https"
            and origin.hostname in ALLOWED_HOSTS
            and not origin.username
            and not origin.password
            and not origin.path
            and not origin.query
            and not origin.fragment
            and (origin.port is None or 1 <= origin.port <= 65535)
            and f"https://{origin.netloc}" == FDS_AUTH_ORIGIN
        )
    except ValueError as exc:
        raise ImproperlyConfigured("Invalid FDS_AUTH_ORIGIN") from exc
    if not valid_origin:
        raise ImproperlyConfigured("FDS_AUTH_ORIGIN must be an allowed HTTPS origin")
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = required("FDS_EMAIL_HOST")
    EMAIL_HOST_USER = required("FDS_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = required("FDS_EMAIL_HOST_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 10
    DEFAULT_FROM_EMAIL = required("FDS_EMAIL_FROM")
    validate_email(DEFAULT_FROM_EMAIL)
