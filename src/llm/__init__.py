"""LLM adapters and research-focused prompt helpers."""

from src.llm.ollama_client import OllamaTextGenerator
from src.llm.research_assistant import LLMResearchAssistant

__all__ = ["LLMResearchAssistant", "OllamaTextGenerator"]
