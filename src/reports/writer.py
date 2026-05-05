import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.core.schemas import Finding, ResearchReport, Source


@dataclass(frozen=True)
class ReportPaths:
    markdown: Path
    json: Path


class ResearchReportWriter:
    def __init__(self, reports_dir: Path | str) -> None:
        self.reports_dir = Path(reports_dir)

    def save(self, report: ResearchReport) -> ReportPaths:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        base_name = self._report_base_name(report.topic)

        markdown_path = self.reports_dir / f"{base_name}.md"
        json_path = self.reports_dir / f"{base_name}.json"

        markdown_path.write_text(self._to_markdown(report), encoding="utf-8")
        json_path.write_text(
            json.dumps(asdict(report), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        return ReportPaths(markdown=markdown_path, json=json_path)

    @classmethod
    def _report_base_name(cls, topic: str) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
        return f"{timestamp}-{slug or 'research'}"

    def _to_markdown(self, report: ResearchReport) -> str:
        title = report.title or f"Research report: {report.topic}"
        sections = [
            f"# {title}",
            f"**Topic:** {report.topic}",
            self._summary_section(report),
            self._findings_section(report.findings),
            self._sources_section(report.sources),
        ]
        return "\n\n".join(section for section in sections if section).strip() + "\n"

    @staticmethod
    def _summary_section(report: ResearchReport) -> str:
        summary = report.summary or report.current_summary
        if not summary:
            return ""

        parts = ["## Summary", summary]
        if report.previous_summary:
            parts.extend(["## Previous Context", report.previous_summary])
        return "\n\n".join(parts)

    @staticmethod
    def _findings_section(findings: list[Finding]) -> str:
        if not findings:
            return ""

        lines = ["## Findings"]
        for index, finding in enumerate(findings, start=1):
            source = finding.source.title or finding.source.url or "Unknown source"
            lines.append(f"{index}. {finding.claim}  \n   Source: {source}")
        return "\n".join(lines)

    @staticmethod
    def _sources_section(sources: list[Source]) -> str:
        if not sources:
            return ""

        lines = ["## Sources"]
        for source in sources:
            label = source.title or source.url or "Untitled source"
            if source.url:
                lines.append(f"- [{label}]({source.url})")
            else:
                lines.append(f"- {label}")
        return "\n".join(lines)
