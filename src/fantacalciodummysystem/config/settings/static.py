# SPDX-License-Identifier: AGPL-3.0-only

"""Database-free analysis and unit tests; never a serving profile."""

from secrets import token_urlsafe

from .base import *  # noqa: F403 - Django settings inheritance

DEBUG = False
SECRET_KEY = token_urlsafe(64)
ALLOWED_HOSTS = ["testserver"]
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
