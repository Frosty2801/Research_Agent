from src.core.schemas import ResearchReport, Source
from src.core.state import AgentState
from src.tools.citations import CitationExtractor, extract_citations

class Reporter:
    def generate_report(self, state: AgentState) -> ResearchReport:
        report = ResearchReport(
            topic=state.topic,
            title=state.title,
            findings=state.findings,
            sources=state.sources,
            summary=state.current_summary or ""
        )
        return report
    
    def extract_citations(self, report: ResearchReport) -> list[Source]:
        return extract_citations(report)
    
