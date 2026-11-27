# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import URLPattern, URLResolver, include, path

from fantacalciodummysystem.accounts import views
from fantacalciodummysystem.accounts.admin import site
from fantacalciodummysystem.api.v1.views import unknown

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1", unknown),
    path("api/v1/", include("fantacalciodummysystem.api.v1.urls")),
    path("auth/register/", views.registration_page),
    path("auth/reset-password/", views.reset_page),
    path("admin/", site.urls),
]
