# SPDX-License-Identifier: AGPL-3.0-only

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "fantacalciodummysystem.accounts"
    label = "accounts"

    def ready(self) -> None:
        from django.contrib.auth.signals import user_logged_in

        from .sessions import stamp_session

        user_logged_in.connect(stamp_session, dispatch_uid="fds.auth.session_stamp")
