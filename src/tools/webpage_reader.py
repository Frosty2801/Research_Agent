from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class _ReadableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return " ".join(self.parts)


class WebPageReaderTool:
    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def read(self, url: str, fallback: str = "") -> str:
        if not url:
            return fallback

        request = Request(
            url,
            headers={"User-Agent": "ResearchAgent/0.1 (+https://example.com)"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                raw_content = response.read()
        except (HTTPError, URLError, TimeoutError, OSError):
            return fallback

        text = raw_content.decode("utf-8", errors="replace")
        if "html" in content_type.lower() or "<html" in text.lower():
            parser = _ReadableHTMLParser()
            parser.feed(text)
            parsed = parser.text()
            return parsed or fallback
        return " ".join(text.split()) or fallback
