from src.core.planner import Planner
from src.core.reporter import Reporter
from src.core.researcher import Researcher
from src.core.schemas import ResearchReport, Source
from src.core.state import AgentState
from src.tools.citations import CitationExtractor


class FakeSearchTool:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def search(self, query: str) -> list[Source]:
        self.queries.append(query)
        return [
            Source(
                title="Primary result",
                url="https://example.com/primary",
                snippet="Primary snippet",
            ),
            Source(
                title="Secondary result",
                url="https://example.com/secondary",
                snippet="Secondary snippet",
            ),
        ]


class FakeReaderTool:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def read(self, url: str, fallback: str = "") -> str:
        self.calls.append((url, fallback))
        return f"Read content for {url}; fallback={fallback}"


class FakeCitationExtractor:
    def __init__(self) -> None:
        self.received_report: ResearchReport | None = None

    def extract_citations(self, report: ResearchReport) -> list[Source]:
        self.received_report = report
        return [Source(title="Citation source", url="https://example.com/citation")]


def test_planner_builds_state_with_topic_previous_summary_and_steps() -> None:
    state = Planner().build_plan("AI safety", previous_summary="Earlier notes")

    assert isinstance(state, AgentState)
    assert state.topic == "AI safety"
    assert state.previous_summary == "Earlier notes"
    assert len(state.Plan) == 7
    assert "AI safety" in state.Plan[0]


def test_researcher_uses_search_results_to_create_findings_and_tool_log() -> None:
    search_tool = FakeSearchTool()
    reader_tool = FakeReaderTool()
    state = AgentState(topic="renewable energy")

    result = Researcher(search_tool, reader_tool).research(state)

    assert result is state
    assert search_tool.queries == ["renewable energy"]
    assert reader_tool.calls == [
        ("https://example.com/primary", "Primary snippet"),
        ("https://example.com/secondary", "Secondary snippet"),
    ]
    assert len(state.findings) == 2
    assert state.findings[0].claim == "Claim about renewable energy based on Primary result"
    assert state.findings[0].source.title == "Primary result"
    assert "Web search results" in state.tool_log[0]
    assert "Read content from https://example.com/primary" in state.tool_log[1]


def test_reporter_builds_report_and_replaces_sources_with_extracted_citations() -> None:
    citation_extractor = FakeCitationExtractor()
    source = Source(title="Original source", url="https://example.com/original")
    state = AgentState(
        topic="climate policy",
        title="Climate Policy Report",
        sources=[source],
        current_summary="A concise summary",
    )

    report = Reporter(citation_extractor).generate_report(state)

    assert report.topic == "climate policy"
    assert report.title == "Climate Policy Report"
    assert report.summary == "A concise summary"
    assert citation_extractor.received_report is report
    assert report.sources == [Source(title="Citation source", url="https://example.com/citation")]


def test_reporter_uses_empty_summary_when_state_has_no_current_summary() -> None:
    report = Reporter(FakeCitationExtractor()).generate_report(AgentState(topic="biology"))

    assert report.summary == ""


def test_research_report_uses_independent_default_lists() -> None:
    first = ResearchReport(topic="first")
    second = ResearchReport(topic="second")

    first.sources.append(Source(title="Only first"))

    assert len(first.sources) == 1
    assert second.sources == []


def test_citation_extractor_returns_placeholder_sources() -> None:
    report = ResearchReport(topic="test topic")

    sources = CitationExtractor().extract_citations(report)

    assert len(sources) == 2
    assert all(isinstance(source, Source) for source in sources)
    assert sources[0].title == "Extracted Source 1"
