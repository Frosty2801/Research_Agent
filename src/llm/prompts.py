from textwrap import dedent

from src.core.schemas import Source
from src.core.state import AgentState


MAX_EVIDENCE_CHARS = 3000


def claim_prompt(topic: str, source: Source, evidence: str) -> str:
    return dedent(
        f"""
        You are extracting one precise research claim.

        Topic: {topic}
        Source title: {source.title}
        Source url: {source.url or "unknown"}

        Evidence:
        {_truncate(evidence, MAX_EVIDENCE_CHARS)}

        Return one concise claim in one sentence. Do not invent facts that are not
        supported by the evidence.
        """
    ).strip()


def title_prompt(topic: str) -> str:
    return dedent(
        f"""
        Write a concise professional research report title for this topic:
        {topic}

        Return only the title.
        """
    ).strip()


def summary_prompt(state: AgentState) -> str:
    findings = "\n".join(
        f"- {finding.claim} (source: {finding.source.title})"
        for finding in state.findings
    )
    previous_summary = state.previous_summary or "No previous summary."

    return dedent(
        f"""
        You are synthesizing a research report summary.

        Topic: {state.topic}

        Previous summary:
        {previous_summary}

        Current findings:
        {findings or "No current findings."}

        Write a clear, compact summary that integrates previous context with new
        findings. Avoid unsupported claims.
        """
    ).strip()


def _truncate(text: str, max_chars: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[:max_chars].rstrip()}..."
