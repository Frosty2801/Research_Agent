from dataclasses import dataclass, field

@dataclass
class ResearchInput:
    topic: str 
    previous_summary: str | None = None

@dataclass
class Source:
    title: str
    url: str = ""
    snippet: str = ""
    date: str = ""
    authors: str = ""
    license: str = ""
    content: str = ""

@dataclass
class Finding:
    claim: str
    evidence: str
    source: Source

@dataclass
class ResearchReport:
    topic: str
    title: str = ""
    summary: str = ""
    previous_summary: str | None = None
    current_summary: str | None = None
    findings: list[Finding] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)
    
