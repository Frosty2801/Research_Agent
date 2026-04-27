from src.core.schemas import Source

class WebSearchTool:
    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider

    def search(self, query: str) -> list[Source]:
        return [
            Source(
                title=f"Result 1 about {query}",
                url="https://example.com/source-1",
                snippet="Initial font about {query} with introductory data"
            ),
            Source(
                title=f"Result 2 about {query}",
                url="https://example.com/source-2",
                snippet="Complementary font about {query} with aditional context"
            )
        ]
