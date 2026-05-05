from src.application.research_workflow import ResearchWorkflow
from src.config.settings import Settings, get_settings
from src.core.planner import Planner
from src.core.reporter import Reporter
from src.core.researcher import Researcher
from src.llm.ollama_client import OllamaTextGenerator
from src.llm.research_assistant import LLMResearchAssistant
from src.memory.json_store import JsonResearchMemory
from src.tools.citations import CitationExtractor
from src.tools.web_search import WebSearchTool
from src.tools.webpage_reader import WebPageReaderTool


def build_research_workflow(settings: Settings | None = None) -> ResearchWorkflow:
    app_settings = settings or get_settings()
    llm_assistant = _build_llm_assistant(app_settings)

    return ResearchWorkflow(
        planner=Planner(),
        researcher=Researcher(
            WebSearchTool(provider=app_settings.default_search_provider),
            WebPageReaderTool(),
            claim_generator=llm_assistant,
        ),
        reporter=Reporter(CitationExtractor()),
        memory=JsonResearchMemory(app_settings.memory_dir),
        summary_builder=llm_assistant,
    )


def _build_llm_assistant(settings: Settings) -> LLMResearchAssistant:
    if settings.llm_provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    text_generator = OllamaTextGenerator(
        model=settings.ollama_model,
        base_url=settings.ollama_api_url,
        temperature=settings.llm_temperature,
    )
    return LLMResearchAssistant(text_generator)
