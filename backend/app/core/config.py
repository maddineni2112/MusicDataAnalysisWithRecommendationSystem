from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://music_user:music_password@localhost:5432/music_intelligence"
    admin_shared_secret: str = "change-me-local-only"
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    artifact_dir: str = "artifacts"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
