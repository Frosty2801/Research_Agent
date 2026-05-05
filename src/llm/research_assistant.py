from src.core.ports import TextGenerator
from src.core.schemas import Source
from src.core.state import AgentState
from src.core.summarizer import SummaryBuilder
from src.llm.prompts import claim_prompt, summary_prompt, title_prompt


class LLMResearchAssistant:
    def __init__(
        self,
        text_generator: TextGenerator,
        fallback: SummaryBuilder | None = None,
    ) -> None:
        self.text_generator = text_generator
        self.fallback = fallback or SummaryBuilder()

    def generate_claim(self, topic: str, source: Source, evidence: str) -> str:
        prompt = claim_prompt(topic, source, evidence)
        claim = self._generate_or_empty(prompt)
        return claim or f"Claim about {topic} based on {source.title}"

    def build_title(self, topic: str) -> str:
        title = self._generate_or_empty(title_prompt(topic))
        return title or self.fallback.build_title(topic)

    def build_summary(self, state: AgentState) -> str:
        summary = self._generate_or_empty(summary_prompt(state))
        return summary or self.fallback.build_summary(state)

    def _generate_or_empty(self, prompt: str) -> str:
        try:
            return self.text_generator.generate(prompt).strip()
        except RuntimeError:
            raise
        except Exception:
            return ""
