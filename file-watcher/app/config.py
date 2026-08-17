from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    WATCH_PATH: str = os.getenv("WATCH_PATH", "/app/inbox")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://backend:8000")
    PROCESSED_PATH: str = os.getenv("PROCESSED_PATH", "/app/processed")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
