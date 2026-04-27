from pydantic import BaseModel, Field

from src.core.schemas import Finding, Source

class agentState(BaseModel):
    topic: str
    Plan: list[str] = Field(default_factory=list)
    tool_log: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    previous_summary: str | None = None
    current_summary: str | None = None
    messages: list[dict] = Field(default_factory=list) 
    