from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    ollama_api_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    llm_provider: str = "ollama"
    llm_temperature: float = 0.2
    default_search_provider: str = "mock"
    tavily_api_key: str | None = None
    memory_dir: Path = Path("src/data/memory")
    reports_dir: Path = Path("src/data/outputs")


@lru_cache
def get_settings() -> Settings:
    return Settings()
