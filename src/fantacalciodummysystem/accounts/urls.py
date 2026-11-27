# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.csrf, name="auth-csrf"),
    path("register/", views.register, name="auth-register"),
    path("verify/", views.verify, name="auth-verify"),
    path("resend/", views.resend, name="auth-resend"),
    path("login/", views.sign_in, name="auth-login"),
    path("logout/", views.sign_out, name="auth-logout"),
    path("password/reset/", views.reset_request, name="auth-reset"),
    path("password/confirm/", views.reset_confirm, name="auth-reset-confirm"),
    path("password/change/", views.password_change, name="auth-password-change"),
]
