from pathlib import Path
from typing import Protocol

from src.core.schemas import ResearchReport


class ResearchMemoryStore(Protocol):
    def load_previous_summary(self, topic: str) -> str | None:
        """Return the latest summary stored for a topic, if available."""
        ...

    def save_report(self, report: ResearchReport) -> Path:
        """Persist the latest report state and return its storage path."""
        ...
