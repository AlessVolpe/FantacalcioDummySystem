# SPDX-License-Identifier: AGPL-3.0-only

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import persistent_secret, postgres, production_hosts

DEBUG = False
SECRET_KEY = persistent_secret("FDS_SECRET_KEY")
ALLOWED_HOSTS = production_hosts()
DATABASES = postgres("FDS_DB_")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Configure trusted proxy headers only when the reverse proxy is deployed.
# No registration or email delivery endpoint is exposed in this PR.
