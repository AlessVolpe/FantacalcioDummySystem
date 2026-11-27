# SPDX-License-Identifier: AGPL-3.0-only

import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .managers import UserManager, canonical_email, validate_identity_email


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True, db_collation="C")
    display_name = models.CharField(max_length=150)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    session_generation = models.UUIDField(default=uuid.uuid4, editable=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email=Lower("email"))
                & models.Q(email__regex=r"^[!-~]+$"),
                name="accounts_user_email_canonical",
            )
        ]

    def clean(self) -> None:
        self.email = canonical_email(self.email)
        validate_identity_email(self.email)
        super().clean()

    def __str__(self) -> str:
        return self.display_name


class AccountToken(models.Model):
    email = models.EmailField(max_length=254, db_collation="C")
    purpose = models.CharField(max_length=16)
    digest = models.CharField(max_length=64, unique=True)
    password_fingerprint = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "purpose"], name="accounts_token_email_purpose"
            )
        ]


class AuthThrottle(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)
