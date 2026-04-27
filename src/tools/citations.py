from src.core.schemas import Source


def render_sources(sources: list[Source]) -> str:
    if not sources:
        return "No sources found."
    
    return "\n".join([f"{source.title}" for source in sources])