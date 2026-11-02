from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "event-backend"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://eventuser:eventpass@db:5432/eventdb"


settings = Settings()
