from dataclasses import dataclass

@dataclass
class ResearchInput:
    topic: str

@dataclass
class Source:
    title: str
    url: str = ""
    snippet: str = ""

@dataclass
class Finding:
    claim: str

@dataclass
class ResearchReport:
    topic: str
