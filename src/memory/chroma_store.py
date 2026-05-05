import re
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.core.schemas import ResearchReport


class ChromaResearchMemory:
    def __init__(
        self,
        persist_dir: Path | str,
        collection_name: str = "research_memory",
        collection: Any | None = None,
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self._collection = collection

    def load_previous_summary(self, topic: str) -> str | None:
        result = self._collection_or_create().get(
            ids=[self._topic_id(topic)],
            include=["documents"],
        )
        documents = result.get("documents", []) if isinstance(result, dict) else []
        summary = documents[0] if documents else None
        return summary if isinstance(summary, str) and summary else None

    def save_report(self, report: ResearchReport) -> Path:
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        summary = report.summary or report.current_summary or ""
        metadata = {
            "topic": report.topic,
            "title": report.title,
            "previous_summary": report.previous_summary or "",
            "updated_at": datetime.now(UTC).isoformat(),
            "report": asdict(report),
        }
        self._collection_or_create().upsert(
            ids=[self._topic_id(report.topic)],
            documents=[summary],
            metadatas=[self._flatten_metadata(metadata)],
        )
        return self.persist_dir

    def _collection_or_create(self):
        if self._collection is not None:
            return self._collection

        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "Chroma memory requires the chromadb package."
            ) from exc

        client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collection = client.get_or_create_collection(self.collection_name)
        return self._collection

    @classmethod
    def _topic_id(cls, topic: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
        return slug or "research"

    @staticmethod
    def _flatten_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
        flattened: dict[str, str | int | float | bool] = {}
        for key, value in metadata.items():
            if isinstance(value, str | int | float | bool):
                flattened[key] = value
            else:
                flattened[key] = str(value)
        return flattened
