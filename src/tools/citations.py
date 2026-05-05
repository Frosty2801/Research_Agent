from src.core.schemas import ResearchReport, Source


class CitationExtractor:
    def extract_citations(self, report: ResearchReport) -> list[Source]:
        sources = [*report.sources, *(finding.source for finding in report.findings)]
        deduped: dict[str, Source] = {}

        for source in sources:
            key = source.url or source.title
            if not key or key in deduped:
                continue
            deduped[key] = source

        return list(deduped.values())
