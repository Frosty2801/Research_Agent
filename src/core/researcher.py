from src.core.schemas import Finding, Source
from src.core.state import AgentState
from src.tools.web_search import WebSearchTool
from src.tools.webpage_reader import WebPageReaderTool


class Researcher:
    def __init__(self, web_search_tool: WebSearchTool, webpage_reader_tool: WebPageReaderTool)-> None:
        self.web_search_tool = web_search_tool
        self.webpage_reader_tool = webpage_reader_tool

    def research(self, state: AgentState) -> AgentState:
        results = self.web_search_tool.search(state.topic)
        state.tool_log.append(f"Web search results: {[result.title for result in results]}")

        for result in results:
            page_content = self.webpage_reader_tool.read(result.url, fallback=result.snippet)
            state.tool_log.append(f"Read content from {result.url}: {page_content[:100]}...")
            state.findings.append(
                Finding(
                    claim=f"Claim about {state.topic} based on {result.title}",
                    evidence=page_content,
                    source=result
                )
            )
        return state