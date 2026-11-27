# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import URLPattern, URLResolver, include, path

from fantacalciodummysystem.accounts import views
from fantacalciodummysystem.accounts.admin import site

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1/auth/", include("fantacalciodummysystem.accounts.urls")),
    path("auth/register/", views.registration_page),
    path("auth/reset-password/", views.reset_page),
    path("admin/", site.urls),
]
