class WebPageReaderTool:
    def read(self, url: str, fallback: str = "") -> str:
        return f"Obtained resume of {url}. {fallback}".strip()
    