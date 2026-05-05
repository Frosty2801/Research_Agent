from src.core.ports import CitationProvider
from src.core.schemas import ResearchReport
from src.core.state import AgentState


class Reporter:
    def __init__(self, citation_extractor: CitationProvider) -> None:
        self.citation_extractor = citation_extractor

    def generate_report(self, state: AgentState) -> ResearchReport:
        report = ResearchReport(
            topic=state.topic,
            title=state.title,
            findings=state.findings,
            sources=state.sources,
            previous_summary=state.previous_summary,
            current_summary=state.current_summary,
            summary=state.current_summary or "",
        )
        report.sources = self.citation_extractor.extract_citations(report)
        return report
