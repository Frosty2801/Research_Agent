from typing import Protocol

from src.core.schemas import ResearchReport, Source
from src.core.state import AgentState


class SearchTool(Protocol):
    def search(self, query: str) -> list[Source]:
        """Return candidate sources for a research query."""
        ...


class PageReader(Protocol):
    def read(self, url: str, fallback: str = "") -> str:
        """Return readable page content for a source URL."""
        ...


class CitationProvider(Protocol):
    def extract_citations(self, report: ResearchReport) -> list[Source]:
        """Return report sources normalized for citation output."""
        ...


class TextGenerator(Protocol):
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        ...


class ClaimGenerator(Protocol):
    def generate_claim(self, topic: str, source: Source, evidence: str) -> str:
        """Extract a research claim from source evidence."""
        ...


class ReportSynthesizer(Protocol):
    def build_title(self, topic: str) -> str:
        """Build a report title for a topic."""
        ...

    def build_summary(self, state: AgentState) -> str:
        """Synthesize the current research state into a summary."""
        ...
