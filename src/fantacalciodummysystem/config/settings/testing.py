# SPDX-License-Identifier: AGPL-3.0-only

from secrets import token_urlsafe

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import postgres

DEBUG = False
SECRET_KEY = token_urlsafe(64)
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = postgres("FDS_TEST_DB_", local=True)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
FDS_AUTH_EMAIL_ENABLED = True
FDS_AUTH_ORIGIN = "http://testserver"
DEFAULT_FROM_EMAIL = "fds@example.invalid"
