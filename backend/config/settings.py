from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Phase 1 ingestion settings (clone + read)."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repos_dir: Path = Field(default=PROJECT_ROOT / "data" / "repos")
    max_file_bytes: int = Field(default=512_000)
    git_clone_depth: int = Field(default=1)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.repos_dir.mkdir(parents=True, exist_ok=True)
    return settings
