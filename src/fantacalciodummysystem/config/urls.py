# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import URLPattern, URLResolver

# Public account and API routes are introduced in later milestone PRs.
urlpatterns: list[URLPattern | URLResolver] = []
