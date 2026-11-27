# SPDX-License-Identifier: AGPL-3.0-only

AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "fantacalciodummysystem.accounts.backends.VerifiedEmailBackend"
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "fantacalciodummysystem.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "fantacalciodummysystem.accounts.sessions.AccountSessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fantacalciodummysystem.config.urls"
WSGI_APPLICATION = "fantacalciodummysystem.config.wsgi.application"
ASGI_APPLICATION = "fantacalciodummysystem.config.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "fantacalciodummysystem.accounts.passwords.PasswordLengthLimit"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
USE_I18N = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_AGE = 7 * 24 * 60 * 60
FDS_SESSION_ABSOLUTE = SESSION_COOKIE_AGE
FDS_SESSION_IDLE = 24 * 60 * 60
FDS_REGISTRATION_TTL = 24 * 60 * 60
FDS_RESET_TTL = 30 * 60
# (per-email, per-IP, window seconds); register/resend share one budget.
FDS_AUTH_LIMITS = {
    "register": (3, 10, 3600),
    "reset": (3, 10, 3600),
    "login": (5, 30, 900),
    "token": (0, 30, 900),
}
FDS_AUTH_EMAIL_ENABLED = False
FDS_AUTH_ORIGIN = ""
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
CSRF_FAILURE_VIEW = "fantacalciodummysystem.accounts.views.csrf_failure"
STATIC_URL = "/static/"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
