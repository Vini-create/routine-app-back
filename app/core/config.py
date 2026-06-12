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

settings = Settings()
