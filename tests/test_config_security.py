"""Fail-fast security invariants for application configuration."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.core.config import Settings


BASE_CONFIG = {
    "app_env": "development",
    "database_url": "postgresql://user:password@localhost/winperium",
    "secret_key": "s" * 64,
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 30,
    "brevo_api_key": "brevo-secret",
    "email_from_name": "Winperium",
    "email_from_address": "noreply@example.com",
    "frontend_url": "https://app.example.com",
    "log_backfill_limit_days": 30,
    "cors_origins": "https://app.example.com,http://localhost:5173",
    "routine_agenda_max_range_days": 90,
    "habits_dashboard_max_range_days": 90,
    "goals_dashboard_max_range_days": 365,
    "future_schedule_limit_years": 5,
    "openai_api_key": "openai-secret",
}


def build_settings(**overrides):
    config = deepcopy(BASE_CONFIG)
    config.update(overrides)
    return Settings(_env_file=None, **config)  # type: ignore[arg-type]


def test_secrets_are_masked_and_only_unwrapped_explicitly() -> None:
    settings = build_settings(
        rate_limit_storage_uri="redis://default:password@redis:6379",
        postgres_password="database-password",
    )
    rendered = repr(settings)

    assert "openai-secret" not in rendered
    assert "brevo-secret" not in rendered
    assert "database-password" not in rendered
    assert "redis://default:password" not in rendered
    assert settings.database_url_value.startswith("postgresql+asyncpg://")
    assert settings.secret_key_value == "s" * 64
    assert settings.openai_api_key_value == "openai-secret"
    assert settings.brevo_api_key_value == "brevo-secret"
    assert settings.rate_limit_storage_uri_value == (
        "redis://default:password@redis:6379"
    )


@pytest.mark.parametrize("length", [0, 1, 32, 63])
def test_secret_key_shorter_than_64_characters_is_rejected(length: int) -> None:
    with pytest.raises(ValidationError, match="at least 64"):
        build_settings(secret_key="x" * length)


def test_only_hs256_is_accepted_for_jwt() -> None:
    with pytest.raises(ValidationError):
        build_settings(algorithm="none")


@pytest.mark.parametrize(
    "cors_origins",
    [
        "*",
        "https://app.example.com,*",
        "javascript:alert(1)",
        "https://app.example.com/path",
        "https://app.example.com?unsafe=true",
    ],
)
def test_unsafe_cors_origins_are_rejected(cors_origins: str) -> None:
    with pytest.raises(ValidationError):
        build_settings(cors_origins=cors_origins)


def test_cors_origins_are_normalized_and_deduplicated() -> None:
    settings = build_settings(
        cors_origins=(
            "https://app.example.com/, http://localhost:5173, "
            "https://app.example.com"
        )
    )

    assert settings.cors_origins_list == [
        "https://app.example.com",
        "http://localhost:5173",
    ]


def test_production_requires_shared_redis_rate_limit_storage() -> None:
    with pytest.raises(ValidationError, match="RATE_LIMIT_STORAGE_URI"):
        build_settings(app_env="production", rate_limit_storage_uri=None)
    with pytest.raises(ValidationError, match="RATE_LIMIT_STORAGE_URI"):
        build_settings(app_env="production", rate_limit_storage_uri=" ")

    production = build_settings(
        app_env="production",
        rate_limit_storage_uri="redis://default:password@redis:6379",
    )
    assert production.app_env == "production"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("access_token_expire_minutes", 4),
        ("access_token_expire_minutes", 1_441),
        ("refresh_token_expire_days", 0),
        ("refresh_token_expire_days", 91),
        ("login_code_expire_minutes", 4),
        ("login_code_expire_minutes", 31),
        ("login_code_max_attempts", 2),
        ("login_code_max_attempts", 11),
    ],
)
def test_authentication_time_and_attempt_limits_are_bounded(
    field: str,
    invalid_value: int,
) -> None:
    with pytest.raises(ValidationError):
        build_settings(**{field: invalid_value})


@pytest.mark.parametrize(
    "frontend_url",
    [
        "javascript:alert(1)",
        "app.example.com",
        "https://app.example.com?redirect=https://evil.example",
        "https://app.example.com#fragment",
    ],
)
def test_frontend_url_must_be_an_absolute_safe_base_url(
    frontend_url: str,
) -> None:
    with pytest.raises(ValidationError):
        build_settings(frontend_url=frontend_url)
