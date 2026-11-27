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
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "fantacalciodummysystem.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "fantacalciodummysystem.api.problems.ApiResponseMiddleware",
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

# Versioned JSON resources. Legacy authentication retains Django CSRF middleware.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["fantacalciodummysystem.api.parsers.StrictJSONParser"],
    "DEFAULT_PAGINATION_CLASS": (
        "fantacalciodummysystem.api.pagination.BoundedPageNumberPagination"
    ),
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "fantacalciodummysystem.api.exceptions.problem_exception_handler",
    "URL_FORMAT_OVERRIDE": None,
}
FDS_API_DOCS_ENABLED = False
SPECTACULAR_SETTINGS = {
    "TITLE": "Fantacalcio Dummy System API",
    "DESCRIPTION": "Versioned application HTTP contract. Same-origin session authentication.",
    "VERSION": "1.0.0",
    "OAS_VERSION": "3.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],
    # Raw JavaScript is supported by drf-spectacular for Swagger UI callbacks.
    # Fetch a fresh masked token before each unsafe request; login rotates it.
    "SWAGGER_UI_SETTINGS": """{
        deepLinking: true,
        persistAuthorization: false,
        validatorUrl: null,
        queryConfigEnabled: false,
        showMutatedRequest: false,
        requestInterceptor: async (request) => {
            const target = new URL(request.url, window.location.href);
            if (target.origin !== window.location.origin) {
                throw new Error("Swagger UI only supports same-origin requests.");
            }
            request.credentials = "same-origin";
            const method = (request.method || "GET").toUpperCase();
            if (["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
                return request;
            }
            if (!target.pathname.startsWith("/api/v1/")) {
                throw new Error("Unsafe Swagger requests must target the v1 API.");
            }
            const response = await fetch("/api/v1/auth/csrf/", {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store",
                redirect: "error",
                headers: {Accept: "application/json"},
            });
            if (!response.ok) {
                throw new Error("Unable to obtain a CSRF token.");
            }
            const {csrfToken} = await response.json();
            if (typeof csrfToken !== "string" || !/^[A-Za-z0-9]{64}$/.test(csrfToken)) {
                throw new Error("Invalid CSRF token response.");
            }
            const headers = new Headers(request.headers);
            headers.set("X-CSRFToken", csrfToken);
            request.headers = Object.fromEntries(headers.entries());
            request.redirect = "error";
            return request;
        },
    }""",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "fantacalciodummysystem.api.v1.schema.add_initial_contract",
    ],
}
