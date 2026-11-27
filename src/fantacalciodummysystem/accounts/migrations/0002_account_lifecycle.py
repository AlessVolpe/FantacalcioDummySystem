# SPDX-License-Identifier: AGPL-3.0-only

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="user",
            name="session_generation",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.CreateModel(
            name="AccountToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(db_collation="C", max_length=254)),
                ("purpose", models.CharField(max_length=16)),
                ("digest", models.CharField(max_length=64, unique=True)),
                ("password_fingerprint", models.CharField(blank=True, max_length=64)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("email", "purpose"),
                        name="accounts_token_email_purpose",
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="AuthThrottle",
            fields=[
                (
                    "key",
                    models.CharField(max_length=64, primary_key=True, serialize=False),
                ),
                ("count", models.PositiveIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
        ),
    ]
