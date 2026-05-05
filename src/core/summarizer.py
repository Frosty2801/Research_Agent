from src.core.state import AgentState


class SummaryBuilder:
    def __init__(self, max_findings: int = 3) -> None:
        self.max_findings = max_findings

    def build_title(self, topic: str) -> str:
        return f"Research report: {topic}"

    def build_summary(self, state: AgentState) -> str:
        findings = state.findings[: self.max_findings]
        if not findings:
            return self._summary_without_findings(state)

        claims = "; ".join(finding.claim for finding in findings)
        summary_parts = [f"Current findings on {state.topic}: {claims}."]
        if state.previous_summary:
            summary_parts.insert(0, f"Previous context: {state.previous_summary}")
        return " ".join(summary_parts)

    @staticmethod
    def _summary_without_findings(state: AgentState) -> str:
        if state.previous_summary:
            return (
                f"No new findings were collected for {state.topic}. "
                f"Previous context remains: {state.previous_summary}"
            )
        return f"No findings were collected for {state.topic}."
