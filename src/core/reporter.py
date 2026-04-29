from src.core.schemas import ResearchReport
from src.core.state import AgentState
from src.tools.citations import CitationExtractor

class Reporter:
    def __init__(self, citation_extractor: CitationExtractor) -> None:
        self.citation_extractor = citation_extractor

    def generate_report(self, state: AgentState) -> ResearchReport:
        report = ResearchReport(
            topic=state.topic,
            title=state.title,
            findings=state.findings,
            sources=state.sources,
            summary=state.current_summary or ""
        )
        report.sources = self.citation_extractor.extract_citations(report)
        return report
