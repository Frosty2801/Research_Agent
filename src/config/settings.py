import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings: 
    openai_api_key: str = ""
    memory_dir: Path = Path("src/data/memory")


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "")
        
    )
