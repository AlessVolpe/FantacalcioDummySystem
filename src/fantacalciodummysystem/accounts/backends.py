# SPDX-License-Identifier: AGPL-3.0-only

from django.contrib.auth.backends import ModelBackend

from .models import User


class VerifiedEmailBackend(ModelBackend):
    def user_can_authenticate(self, user: object) -> bool:
        return (
            isinstance(user, User)
            and user.email_verified_at is not None
            and super().user_can_authenticate(user)
        )
