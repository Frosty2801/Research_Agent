import json
import re
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.core.schemas import ResearchReport


class JsonResearchMemory:
    def __init__(self, memory_dir: Path | str) -> None:
        self.memory_dir = Path(memory_dir)

    def load_previous_summary(self, topic: str) -> str | None:
        path = self._topic_path(topic)
        if not path.exists():
            return None

        data = self._read_json(path)
        summary = data.get("current_summary")
        return summary if isinstance(summary, str) and summary else None

    def save_report(self, report: ResearchReport) -> Path:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        path = self._topic_path(report.topic)
        payload = {
            "topic": report.topic,
            "title": report.title,
            "previous_summary": report.previous_summary,
            "current_summary": report.summary or report.current_summary,
            "updated_at": datetime.now(UTC).isoformat(),
            "report": asdict(report),
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        return path

    def _topic_path(self, topic: str) -> Path:
        return self.memory_dir / f"{self._slugify(topic)}.json"

    @staticmethod
    def _slugify(topic: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
        return slug or "research"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return data if isinstance(data, dict) else {}
