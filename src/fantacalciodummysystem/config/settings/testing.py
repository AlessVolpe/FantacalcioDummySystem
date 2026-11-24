# SPDX-License-Identifier: AGPL-3.0-only

from .base import *  # noqa: F403 - Django settings inheritance
from .environment import postgres

DEBUG = False
SECRET_KEY = "fds-testing-only-not-a-production-secret"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = postgres("FDS_TEST_DB_", local=True)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
