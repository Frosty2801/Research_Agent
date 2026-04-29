from src.core.state import AgentState

class Planner:
    def build_plan(self, topic: str, previous_summary: str | None = None) -> AgentState:
        plan = [
            f"Define the problem: Clearly understand the topic '{topic}'",
            "Gather information: Research and collect relevant data and sources",
            "Analyze the information: Identify patterns, connections, and insights",
            "Formulate a hypothesis: Develop a potential solution or explanation",
            "Test the hypothesis: Design and conduct experiments or simulations",
            "Evaluate results: Assess the outcomes and refine the hypothesis if necessary",
            "Communicate findings: Summarize the results and share with others"
        ]
        return AgentState(
            topic=topic,
            Plan=plan,
            previous_summary=previous_summary
        )

