import asyncio
import os
import subprocess
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.asyncio

MIGRATION_DATABASE = "back_routine_migration_test"
PRE_BILLING_REVISION = "7c85e2a5c931"


async def run_alembic(database_url: str, *arguments: str) -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    await asyncio.to_thread(
        subprocess.run,
        [".venv/bin/alembic", *arguments],
        cwd=os.getcwd(),
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


async def test_billing_migration_backfills_every_existing_user_to_free() -> None:
    configured_url = make_url(os.environ["DATABASE_URL"])
    admin_url = configured_url.set(database="postgres")
    migration_url = configured_url.set(database=MIGRATION_DATABASE)
    rendered_migration_url = migration_url.render_as_string(hide_password=False)

    admin_engine = create_async_engine(
        admin_url.render_as_string(hide_password=False),
        isolation_level="AUTOCOMMIT",
    )
    async with admin_engine.connect() as connection:
        await connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :database AND pid <> pg_backend_pid()"
            ),
            {"database": MIGRATION_DATABASE},
        )
        await connection.execute(
            text(f'DROP DATABASE IF EXISTS "{MIGRATION_DATABASE}"')
        )
        await connection.execute(text(f'CREATE DATABASE "{MIGRATION_DATABASE}"'))

    migration_engine = create_async_engine(rendered_migration_url)
    try:
        await run_alembic(
            rendered_migration_url,
            "upgrade",
            PRE_BILLING_REVISION,
        )
        existing_user_id = uuid4()
        async with migration_engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO users (
                        id,
                        email,
                        display_name,
                        timezone,
                        language,
                        is_active,
                        signature_plan,
                        is_verified,
                        has_password,
                        pending_deletion
                    )
                    VALUES (
                        :id,
                        :email,
                        'Legacy User',
                        'America/Sao_Paulo',
                        'portuguese_br',
                        true,
                        'pro',
                        true,
                        true,
                        false
                    )
                    """
                ),
                {
                    "id": existing_user_id,
                    "email": "legacy-billing@example.com",
                },
            )

        await run_alembic(rendered_migration_url, "upgrade", "head")

        async with migration_engine.connect() as connection:
            legacy_plan = await connection.scalar(
                text("SELECT signature_plan FROM users WHERE id = :id"),
                {"id": existing_user_id},
            )
            account = (
                await connection.execute(
                    text(
                        """
                        SELECT
                            plan_code,
                            subscription_status,
                            billing_provider,
                            provider_customer_id,
                            provider_subscription_id
                        FROM billing_accounts
                        WHERE user_id = :id
                        """
                    ),
                    {"id": existing_user_id},
                )
            ).one()

        assert legacy_plan == "free"
        assert account.plan_code == "free"
        assert account.subscription_status == "active"
        assert account.billing_provider == "internal"
        assert account.provider_customer_id is None
        assert account.provider_subscription_id is None

        await run_alembic(rendered_migration_url, "check")
        await run_alembic(
            rendered_migration_url,
            "downgrade",
            PRE_BILLING_REVISION,
        )
        async with migration_engine.connect() as connection:
            remaining_tables = set(
                (
                    await connection.execute(
                        text(
                            """
                            SELECT table_name
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                              AND table_name IN (
                                  'billing_accounts',
                                  'ai_usage_events'
                              )
                            """
                        )
                    )
                ).scalars()
            )
        assert remaining_tables == set()
    finally:
        await migration_engine.dispose()
        async with admin_engine.connect() as connection:
            await connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :database AND pid <> pg_backend_pid()"
                ),
                {"database": MIGRATION_DATABASE},
            )
            await connection.execute(
                text(f'DROP DATABASE IF EXISTS "{MIGRATION_DATABASE}"')
            )
        await admin_engine.dispose()
