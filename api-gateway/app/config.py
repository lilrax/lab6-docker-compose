from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int = Field(ge=1, le=65535)
    storage_url: str
    request_timeout: float = Field(gt=0)
    log_level: Literal["debug", "info", "warning", "error", "critical"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GATEWAY_",
        extra="ignore",
    )
