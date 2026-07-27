from decimal import Decimal
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: SecretStr
    postgres_user: str | None = None
    postgres_password: SecretStr | None = None
    postgres_db: str | None = None
    secret_key: SecretStr
    algorithm: Literal["HS256"]
    access_token_expire_minutes: int = Field(ge=5, le=1_440)
    refresh_token_expire_days: int = Field(ge=1, le=90)
    brevo_api_key: SecretStr
    email_from_name: str
    email_from_address: str
    frontend_url: str
    log_backfill_limit_days: int
    cors_origins: str
    sql_echo: bool = False
    rate_limit_storage_uri: SecretStr | None = None
    routine_agenda_max_range_days: int
    habits_dashboard_max_range_days: int
    goals_dashboard_max_range_days: int
    future_schedule_limit_years: int
    google_client_id: str | None = None
    login_code_expire_minutes: int = Field(default=10, ge=5, le=30)
    login_code_max_attempts: int = Field(default=5, ge=3, le=10)
    openai_api_key: SecretStr
    ai_router_model: str = "gpt-4o-mini"
    ai_alfred_model: str = "gpt-4o-mini"
    ai_feedbacker_model: str = "gpt-5"
    ai_critic_model: str = "gpt-4o-mini"
    ai_embedding_model: str = "intfloat/multilingual-e5-small"
    ai_embedding_device: str = "cpu"
    ai_embedding_batch_size: int = Field(default=16, ge=1, le=128)
    ai_rag_candidate_limit: int = Field(default=12, ge=4, le=50)
    ai_rag_evidence_limit: int = Field(default=4, ge=1, le=8)
    ai_model_timeout_seconds: float = Field(default=45.0, ge=5.0, le=180.0)
    ai_model_max_retries: int = Field(default=2, ge=0, le=5)
    ai_request_timeout_seconds: float = Field(default=110.0, ge=15.0, le=300.0)
    ai_reservation_timeout_seconds: int = Field(default=120, ge=30, le=900)
    ai_message_retention_days: int = Field(default=90, ge=30, le=365)
    ai_patch_retention_days: int = Field(default=90, ge=30, le=365)
    ai_expired_patch_grace_days: int = Field(default=7, ge=1, le=30)
    ai_deleted_conversation_retention_days: int = Field(
        default=30,
        ge=7,
        le=90,
    )
    ai_intervention_retention_days: int = Field(default=180, ge=90, le=730)
    ai_observability_retention_days: int = Field(default=400, ge=365, le=2_555)
    ai_global_daily_cost_limit_usd: Decimal = Field(
        default=Decimal("10.00"),
        gt=0,
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_async_database_url(cls, value: str | SecretStr) -> str:
        # Railway exposes a standard PostgreSQL URL. This application uses the
        # asyncpg driver, so add the SQLAlchemy async driver when it is omitted.
        database_url = (
            value.get_secret_value() if isinstance(value, SecretStr) else str(value)
        )

        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        if database_url.startswith("postgresql://"):
            return database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return database_url

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_strength(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 64:
            raise ValueError("SECRET_KEY must contain at least 64 characters")
        return value

    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, value: str) -> str:
        normalized = value.strip().rstrip("/")
        parsed = urlsplit(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("FRONTEND_URL must be an absolute HTTP(S) URL")
        if parsed.query or parsed.fragment:
            raise ValueError("FRONTEND_URL cannot contain a query or fragment")
        return normalized

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [origin.strip().rstrip("/") for origin in value.split(",")]
        origins = [origin for origin in origins if origin]
        if not origins:
            raise ValueError("CORS_ORIGINS must contain at least one origin")
        for origin in origins:
            if origin == "*":
                raise ValueError("CORS_ORIGINS cannot contain a wildcard")
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError(
                    "Each CORS origin must be an HTTP(S) origin without path, "
                    "query or fragment"
                )
        return ",".join(dict.fromkeys(origins))

    @model_validator(mode="after")
    def require_production_redis(self) -> "Settings":
        redis_uri = (
            self.rate_limit_storage_uri.get_secret_value().strip()
            if self.rate_limit_storage_uri is not None
            else ""
        )
        if self.app_env == "production" and not redis_uri:
            raise ValueError(
                "RATE_LIMIT_STORAGE_URI is required when APP_ENV=production"
            )
        return self

    @property
    def database_url_value(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def secret_key_value(self) -> str:
        return self.secret_key.get_secret_value()

    @property
    def brevo_api_key_value(self) -> str:
        return self.brevo_api_key.get_secret_value()

    @property
    def openai_api_key_value(self) -> str:
        return self.openai_api_key.get_secret_value()

    @property
    def rate_limit_storage_uri_value(self) -> str | None:
        if self.rate_limit_storage_uri is None:
            return None
        value = self.rate_limit_storage_uri.get_secret_value().strip()
        return value or None

    @property
    def cors_origins_list(self) -> list[str]:
        return self.cors_origins.split(",")


settings = Settings()  # type: ignore[call-arg]
