import argparse
import sys
from collections.abc import Sequence

from src.application.factory import build_research_workflow
from src.config.settings import get_settings
from src.reports.writer import ResearchReportWriter


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="research-agent",
        description="Run a research workflow for a topic.",
    )
    parser.add_argument("topic", nargs="+", help="Topic to research.")
    args = parser.parse_args(argv)

    topic = " ".join(args.topic).strip()
    if not topic:
        parser.error("topic cannot be empty")

    try:
        settings = get_settings()
        workflow = build_research_workflow(settings)
        report = workflow.run(topic)
        paths = ResearchReportWriter(settings.reports_dir).save(report)
    except Exception as exc:
        print(f"Research failed: {exc}", file=sys.stderr)
        return 1

    print(f"Report title: {report.title}")
    print(f"Markdown: {paths.markdown}")
    print(f"JSON: {paths.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
