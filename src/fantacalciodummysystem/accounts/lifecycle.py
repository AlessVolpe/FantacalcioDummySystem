# SPDX-License-Identifier: AGPL-3.0-only

import hashlib
import logging
from datetime import timedelta
from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, connection, transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from .models import AccountToken, User

REGISTER = "register"
RESET = "reset"
logger = logging.getLogger(__name__)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fingerprint(user: User) -> str:
    return digest(f"{user.password}:{user.session_generation}")


def lock_email(email: str) -> None:
    # Serialize issuance, consumption and password changes even before a User
    # exists. A collision only causes unrelated requests to wait briefly.
    key = int.from_bytes(
        hashlib.sha256(f"fds.auth:{email}".encode()).digest()[:8],
        "big",
        signed=True,
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [key])


def eligible(user: User | None, purpose: str) -> bool:
    if purpose == REGISTER:
        return user is None
    if purpose == RESET:
        return bool(user and user.is_active and user.email_verified_at is not None)
    raise ValueError("Unknown token purpose")


def issue(email: str, purpose: str) -> None:
    with transaction.atomic():
        lock_email(email)
        user = User.objects.filter(email=email).first()
        if not eligible(user, purpose):
            return
        token = token_urlsafe(32)
        duration = (
            settings.FDS_REGISTRATION_TTL
            if purpose == REGISTER
            else settings.FDS_RESET_TTL
        )
        AccountToken.objects.update_or_create(
            email=email,
            purpose=purpose,
            defaults={
                "digest": digest(token),
                "password_fingerprint": fingerprint(user) if user else "",
                "expires_at": timezone.now() + timedelta(seconds=duration),
            },
        )
    # Do not hold database locks during external I/O. A failed delivery is
    # indistinguishable from an ineligible address; a resend replaces the token.
    path = "register" if purpose == REGISTER else "reset-password"
    link = f"{settings.FDS_AUTH_ORIGIN}/auth/{path}/#token={token}"
    try:
        sent = send_mail(
            "Complete your FDS account request",
            f"Open this link to continue:\n\n{link}\n\n"
            "If you did not request this, ignore this message.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        if sent != 1:
            logger.warning("Account email delivery failed")
    except Exception:
        # SMTP/provider exceptions may include addresses or credentials.
        logger.warning("Account email delivery failed")


def locked_token(raw: str, purpose: str) -> AccountToken | None:
    token_digest = digest(raw)
    initial = AccountToken.objects.filter(digest=token_digest, purpose=purpose).first()
    if initial is None:
        return None
    lock_email(initial.email)
    return (
        AccountToken.objects.select_for_update()
        .filter(digest=token_digest, purpose=purpose, expires_at__gt=timezone.now())
        .first()
    )


def register(raw: str, display_name: str, password: str) -> bool:
    with transaction.atomic():
        token = locked_token(raw, REGISTER)
        if token is None or User.objects.filter(email=token.email).exists():
            return False
        candidate = User(email=token.email, display_name=display_name)
        validate_password(password, candidate)
        try:
            with transaction.atomic():
                User.objects.create_user(
                    token.email,
                    password,
                    display_name=display_name,
                    email_verified_at=timezone.now(),
                )
        except IntegrityError:
            if User.objects.filter(email=token.email).exists():
                return False
            raise
        token.delete()
        return True


def reset(raw: str, password: str) -> bool:
    with transaction.atomic():
        token = locked_token(raw, RESET)
        if token is None:
            return False
        user = User.objects.select_for_update().filter(email=token.email).first()
        if user is None or not eligible(user, RESET):
            return False
        if not constant_time_compare(token.password_fingerprint, fingerprint(user)):
            return False
        validate_password(password, user)
        user.set_password(password)
        user.save(update_fields=["password"])
        token.delete()
        return True


class InvalidCredentials(ValidationError):
    pass


def change_password(user: User, current: str, password: str) -> User:
    with transaction.atomic():
        lock_email(user.email)
        fresh = User.objects.select_for_update().get(pk=user.pk)
        if not eligible(fresh, RESET) or not fresh.check_password(current):
            raise InvalidCredentials("Invalid current credentials.")
        validate_password(password, fresh)
        fresh.set_password(password)
        fresh.save(update_fields=["password"])
        AccountToken.objects.filter(email=fresh.email, purpose=RESET).delete()
        return fresh
