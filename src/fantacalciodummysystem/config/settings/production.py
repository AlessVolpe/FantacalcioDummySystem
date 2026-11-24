# SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import postgres, production_hosts, required

DEBUG = False
SECRET_KEY = required("FDS_SECRET_KEY")
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("fds-"):
    raise ImproperlyConfigured("FDS_SECRET_KEY must be a strong production secret")
ALLOWED_HOSTS = production_hosts()
DATABASES = postgres("FDS_DB_")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Configure trusted proxy headers only when the reverse proxy is deployed.
# No registration or email delivery endpoint is exposed in this PR.
