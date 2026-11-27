# SPDX-License-Identifier: AGPL-3.0-only

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import persistent_secret, postgres

DEBUG = True
SECRET_KEY = persistent_secret("FDS_DEV_SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
DATABASES = postgres("FDS_DEV_DB_", local=True)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
FDS_AUTH_EMAIL_ENABLED = True
FDS_AUTH_ORIGIN = "http://localhost:8000"
DEFAULT_FROM_EMAIL = "fds@example.invalid"
