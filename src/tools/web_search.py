from src.core.schemas import Source


class WebSearchTool:
    def __init__(self, provider: str = "mock", max_results: int = 5) -> None:
        self.provider = provider
        self.max_results = max_results

    def search(self, query: str) -> list[Source]:
        if self.provider == "mock":
            return self._mock_search(query)
        if self.provider == "tavily":
            return self._tavily_search(query)
        raise ValueError(f"Unsupported search provider: {self.provider}")

    def _mock_search(self, query: str) -> list[Source]:
        return [
            Source(
                title=f"Result 1 about {query}",
                url="https://example.com/source-1",
                snippet=f"Initial source about {query} with introductory data",
            ),
            Source(
                title=f"Result 2 about {query}",
                url="https://example.com/source-2",
                snippet=f"Complementary source about {query} with additional context",
            ),
        ][: self.max_results]

    def _tavily_search(self, query: str) -> list[Source]:
        try:
            from langchain_tavily import TavilySearch
        except ImportError as exc:
            raise RuntimeError(
                "Tavily search requires the langchain-tavily package."
            ) from exc

        tool = TavilySearch(max_results=self.max_results)
        response = tool.invoke({"query": query})
        results = (
            response.get("results", response)
            if isinstance(response, dict)
            else response
        )

        sources: list[Source] = []
        for item in results or []:
            if not isinstance(item, dict):
                continue
            sources.append(
                Source(
                    title=item.get("title") or item.get("url") or "Untitled source",
                    url=item.get("url", ""),
                    snippet=item.get("content") or item.get("snippet") or "",
                    date=item.get("published_date", ""),
                )
            )
        return sources
