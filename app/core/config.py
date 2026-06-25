from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
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
    rate_limit_storage_uri: str | None
    routine_agenda_max_range_days: int
    habits_dashboard_max_range_days: int
    goals_dashboard_max_range_days: int
    future_schedule_limit_years: int

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

settings = Settings()
