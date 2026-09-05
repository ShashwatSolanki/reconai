from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the investigation provider."""

    investigation_provider: Literal["mock", "openai"] = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
