from textwrap import shorten

from src.core.ports import ClaimGenerator, PageReader, SearchTool
from src.core.schemas import Finding, Source
from src.core.state import AgentState


class Researcher:
    def __init__(
        self,
        web_search_tool: SearchTool,
        webpage_reader_tool: PageReader,
        claim_generator: ClaimGenerator | None = None,
    ) -> None:
        self.web_search_tool = web_search_tool
        self.webpage_reader_tool = webpage_reader_tool
        self.claim_generator = claim_generator

    def research(self, state: AgentState) -> AgentState:
        results = self.web_search_tool.search(state.topic)
        state.tool_log.append(
            f"Web search results: {[result.title for result in results]}"
        )
        state.sources.extend(results)

        for result in results:
            page_content = self.webpage_reader_tool.read(
                result.url,
                fallback=result.snippet,
            )
            preview = shorten(page_content, width=100, placeholder="...")
            state.tool_log.append(f"Read content from {result.url}: {preview}")
            state.findings.append(
                Finding(
                    claim=self._generate_claim(state.topic, result, page_content),
                    evidence=page_content,
                    source=result,
                )
            )
        return state

    def _generate_claim(self, topic: str, source: Source, evidence: str) -> str:
        if self.claim_generator is None:
            return f"Claim about {topic} based on {source.title}"
        return self.claim_generator.generate_claim(topic, source, evidence)
