# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import include, path, re_path

from . import docs, views

urlpatterns = [
    path("auth/me/", views.me, name="auth-me"),
    path("auth/", include("fantacalciodummysystem.accounts.urls")),
    path("health/live/", views.LivenessView.as_view(), name="health-live"),
    path("health/ready/", views.ReadinessView.as_view(), name="health-ready"),
    path("schema/", docs.schema, name="api-schema"),
    path("docs/", docs.swagger, name="api-docs"),
    path("redoc/", docs.redoc, name="api-redoc"),
    # Keep API 404s JSON and never redirect an unsafe missing-slash request.
    re_path(r"^.*$", views.unknown, name="api-not-found"),
]
