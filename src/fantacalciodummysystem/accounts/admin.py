# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse

from .managers import canonical_email, validate_identity_email
from .models import User
from .throttles import login_budget

if TYPE_CHECKING:
    BaseUserAdmin = admin.ModelAdmin[User]
else:
    BaseUserAdmin = admin.ModelAdmin


class AccountAdminAuthenticationForm(AdminAuthenticationForm):
    # Django's default UsernameField applies NFKC normalization; retain FDS's
    # stricter ASCII identity policy on the administrative login as well.
    username = forms.CharField(
        label="Email",
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )

    def clean_username(self) -> str:
        email = canonical_email(self.cleaned_data["username"])
        validate_identity_email(email)
        return email


class AccountAdminSite(admin.AdminSite):
    login_form = AccountAdminAuthenticationForm

    def login(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        if request.method != "POST":
            return super().login(request, extra_context)
        email = canonical_email(request.POST.get("username", ""))[:254]
        if len(request.POST.get("password", "")) > 128:
            return HttpResponse("Invalid credentials", status=400)
        with login_budget(request, email) as budget:
            if not budget.allowed:
                return HttpResponse("Too many attempts", status=429)
            response = super().login(request, extra_context)
            budget.succeeded = bool(
                response.status_code == 302
                and request.user.is_authenticated
                and request.user.is_staff
            )
            if budget.succeeded:
                request.session.cycle_key()
            return response

    # Django may redirect or return an error response, not just a template.
    def password_change(  # type: ignore[override]
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        user = request.user
        if request.method != "POST" or not isinstance(user, User):
            return super().password_change(request, extra_context)
        if len(request.POST.get("old_password", "")) > 128:
            return HttpResponse("Invalid credentials", status=400)
        with login_budget(request, user.email) as budget:
            if not budget.allowed:
                return HttpResponse("Too many attempts", status=429)
            # Django's password-change form saves the user instance. Lock and
            # reload it so an activation change cannot be overwritten.
            fresh = User.objects.select_for_update().get(pk=user.pk)
            if (
                not fresh.is_active
                or fresh.session_generation != user.session_generation
            ):
                return HttpResponse("Authentication required", status=403)
            request.user = fresh
            response = super().password_change(request, extra_context)
            # A successful Django password-change form redirects. Count other
            # outcomes conservatively, including invalid new passwords.
            budget.succeeded = response.status_code == 302
            return response


class AccountAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "display_name",
        "is_active",
        "email_verified_at",
        "is_staff",
    )
    search_fields = ("email", "display_name")
    fields = (
        "id",
        "email",
        "display_name",
        "email_verified_at",
        "date_joined",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    readonly_fields = (
        "id",
        "email",
        "display_name",
        "email_verified_at",
        "date_joined",
        "is_staff",
        "is_superuser",
    )
    actions = None

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: User | None = None
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: User | None = None
    ) -> bool:
        return bool(
            request.user.is_superuser and (obj is None or obj.pk != request.user.pk)
        )

    def save_model(
        self, request: HttpRequest, obj: User, form: ModelForm[User], change: bool
    ) -> None:
        # Never overwrite a concurrently updated password or identity field.
        with transaction.atomic():
            fresh = User.objects.select_for_update().get(pk=obj.pk)
            if fresh.is_active != obj.is_active:
                fresh.is_active = obj.is_active
                fresh.session_generation = uuid.uuid4()
                fresh.save(update_fields=["is_active", "session_generation"])


site = AccountAdminSite(name="fds_admin")
site.register(User, AccountAdmin)
