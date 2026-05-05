from src.core.planner import Planner
from src.core.reporter import Reporter
from src.core.researcher import Researcher
from src.core.schemas import ResearchReport
from src.core.ports import ReportSynthesizer
from src.core.summarizer import SummaryBuilder
from src.memory.store import ResearchMemoryStore


class ResearchWorkflow:
    def __init__(
        self,
        planner: Planner,
        researcher: Researcher,
        reporter: Reporter,
        memory: ResearchMemoryStore,
        summary_builder: ReportSynthesizer | None = None,
    ) -> None:
        self.planner = planner
        self.researcher = researcher
        self.reporter = reporter
        self.memory = memory
        self.summary_builder = summary_builder or SummaryBuilder()

    def run(self, topic: str) -> ResearchReport:
        previous_summary = self.memory.load_previous_summary(topic)
        state = self.planner.build_plan(topic, previous_summary=previous_summary)

        researched_state = self.researcher.research(state)
        if not researched_state.title:
            researched_state.title = self.summary_builder.build_title(topic)
        if not researched_state.current_summary:
            researched_state.current_summary = self.summary_builder.build_summary(
                researched_state
            )

        report = self.reporter.generate_report(researched_state)
        self.memory.save_report(report)
        return report
