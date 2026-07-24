from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://music_user:music_password@localhost:5432/music_intelligence"
    admin_shared_secret: str = "change-me-local-only"
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    artifact_dir: str = "artifacts"
    backend_cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8010,http://127.0.0.1:8010"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
