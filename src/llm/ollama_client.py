class OllamaTextGenerator:
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.2,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self._client = None

    def generate(self, prompt: str) -> str:
        client = self._get_client()
        response = client.invoke(prompt)
        content = getattr(response, "content", response)
        return str(content).strip()

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from langchain_ollama import ChatOllama
        except ImportError as exc:
            raise RuntimeError(
                "Ollama support requires the langchain-ollama package."
            ) from exc

        self._client = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
        )
        return self._client
