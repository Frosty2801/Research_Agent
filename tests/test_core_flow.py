import json

from src.application.factory import build_research_workflow
from src.application.research_workflow import ResearchWorkflow
from src.config.settings import Settings
from src.core.planner import Planner
from src.core.reporter import Reporter
from src.core.researcher import Researcher
from src.core.schemas import Finding, ResearchReport, Source
from src.core.state import AgentState
from src.core.summarizer import SummaryBuilder
from src.llm.research_assistant import LLMResearchAssistant
from src.memory.json_store import JsonResearchMemory
from src.tools import webpage_reader
from src.tools.citations import CitationExtractor
from src.tools.webpage_reader import WebPageReaderTool
from src.tools.web_search import WebSearchTool


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


class FakeTextGenerator:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


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
    assert state.sources == [
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
    assert state.findings[0].claim == "Claim about renewable energy based on Primary result"
    assert state.findings[0].source.title == "Primary result"
    assert "Web search results" in state.tool_log[0]
    assert "Read content from https://example.com/primary" in state.tool_log[1]


def test_researcher_uses_claim_generator_when_available() -> None:
    search_tool = FakeSearchTool()
    reader_tool = FakeReaderTool()
    claim_generator = LLMResearchAssistant(FakeTextGenerator(["Generated claim"]))
    state = AgentState(topic="renewable energy")

    Researcher(search_tool, reader_tool, claim_generator).research(state)

    assert state.findings[0].claim == "Generated claim"


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
    assert report.current_summary == "A concise summary"
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


def test_citation_extractor_deduplicates_report_and_finding_sources() -> None:
    source = Source(title="Original", url="https://example.com/original")
    duplicate = Source(title="Duplicate", url="https://example.com/original")
    finding_source = Source(title="Finding source", url="https://example.com/finding")
    report = ResearchReport(
        topic="test topic",
        sources=[source, duplicate],
        findings=[
            Finding(
                claim="A claim",
                evidence="Evidence",
                source=finding_source,
            )
        ],
    )

    sources = CitationExtractor().extract_citations(report)

    assert len(sources) == 2
    assert sources == [source, finding_source]


def test_web_search_mock_provider_respects_max_results() -> None:
    results = WebSearchTool(max_results=1).search("soil health")

    assert len(results) == 1
    assert results[0].title == "Result 1 about soil health"
    assert results[0].url == "https://example.com/source-1"


def test_webpage_reader_extracts_text_from_html(monkeypatch) -> None:
    class FakeResponse:
        headers = {"Content-Type": "text/html; charset=utf-8"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            return None

        def read(self) -> bytes:
            return (
                b"<html><script>x()</script><body><h1>Title</h1>"
                b"<p>Main text</p></body></html>"
            )

    def fake_urlopen(request, timeout):
        return FakeResponse()

    monkeypatch.setattr(webpage_reader, "urlopen", fake_urlopen)

    content = WebPageReaderTool().read("https://example.com/article", fallback="Fallback")

    assert content == "Title Main text"


def test_webpage_reader_returns_fallback_on_error(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        raise OSError("network unavailable")

    monkeypatch.setattr(webpage_reader, "urlopen", fake_urlopen)

    content = WebPageReaderTool().read("https://example.com/article", fallback="Fallback")

    assert content == "Fallback"


def test_research_memory_saves_and_loads_summary(tmp_path) -> None:
    memory = JsonResearchMemory(tmp_path)
    report = ResearchReport(
        topic="Climate Policy",
        title="Climate Policy Report",
        summary="Current synthesis",
        previous_summary="Earlier synthesis",
    )

    path = memory.save_report(report)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "climate-policy.json"
    assert data["topic"] == "Climate Policy"
    assert data["current_summary"] == "Current synthesis"
    assert memory.load_previous_summary("Climate Policy") == "Current synthesis"


def test_summary_builder_combines_previous_memory_with_current_findings() -> None:
    state = AgentState(
        topic="climate policy",
        previous_summary="Earlier synthesis",
        findings=[
            Finding(
                claim="Emissions targets are expanding",
                evidence="Evidence",
                source=Source(title="Policy source"),
            )
        ],
    )

    summary = SummaryBuilder().build_summary(state)

    assert "Previous context: Earlier synthesis" in summary
    assert "Current findings on climate policy" in summary
    assert "Emissions targets are expanding" in summary


def test_llm_research_assistant_builds_claim_title_and_summary() -> None:
    text_generator = FakeTextGenerator(
        [
            "Claim from evidence",
            "Generated title",
            "Generated summary",
        ]
    )
    assistant = LLMResearchAssistant(text_generator)
    state = AgentState(
        topic="climate policy",
        findings=[
            Finding(
                claim="A finding",
                evidence="Evidence",
                source=Source(title="Policy source"),
            )
        ],
    )

    claim = assistant.generate_claim("climate policy", Source(title="Source"), "Evidence")
    title = assistant.build_title("climate policy")
    summary = assistant.build_summary(state)

    assert claim == "Claim from evidence"
    assert title == "Generated title"
    assert summary == "Generated summary"
    assert len(text_generator.prompts) == 3


def test_research_workflow_loads_previous_summary_and_saves_new_report(tmp_path) -> None:
    memory = JsonResearchMemory(tmp_path)
    memory.save_report(
        ResearchReport(
            topic="Climate Policy",
            summary="Earlier synthesis",
        )
    )
    search_tool = FakeSearchTool()
    reader_tool = FakeReaderTool()
    workflow = ResearchWorkflow(
        planner=Planner(),
        researcher=Researcher(search_tool, reader_tool),
        reporter=Reporter(FakeCitationExtractor()),
        memory=memory,
    )

    report = workflow.run("Climate Policy")

    assert report.previous_summary == "Earlier synthesis"
    assert report.title == "Research report: Climate Policy"
    assert "Previous context: Earlier synthesis" in report.summary
    assert memory.load_previous_summary("Climate Policy") == report.summary


def test_factory_builds_workflow_from_settings(tmp_path) -> None:
    settings = Settings(
        default_search_provider="mock",
        memory_dir=tmp_path,
        llm_provider="ollama",
        ollama_model="llama3.1",
        ollama_api_url="http://localhost:11434",
    )

    workflow = build_research_workflow(settings)

    assert isinstance(workflow, ResearchWorkflow)
