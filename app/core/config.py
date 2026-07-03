from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    brevo_api_key: str
    email_from_name: str
    email_from_address: str
    frontend_url: str
    log_backfill_limit_days: int
    cors_origins: str
    sql_echo: bool = False
    rate_limit_storage_uri: str | None = None
    routine_agenda_max_range_days: int
    habits_dashboard_max_range_days: int
    goals_dashboard_max_range_days: int
    future_schedule_limit_years: int

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_async_database_url(cls, value: str) -> str:
        # Railway exposes a standard PostgreSQL URL. This application uses the
        # asyncpg driver, so add the SQLAlchemy async driver when it is omitted.
        database_url = str(value)

        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        if database_url.startswith("postgresql://"):
            return database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return database_url

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

settings = Settings()
