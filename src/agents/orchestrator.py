from .coverage_agent import CoverageAgent
from .gherkin_agent import GherkinAgent
from .script_agent import ScriptAgent


class OrchestratorAgent:
    """Coordinates the agents to deliver Gherkin, scripts, and coverage analysis."""

    def __init__(self) -> None:
        self.gherkin_agent = GherkinAgent()
        self.script_agent = ScriptAgent()
        self.coverage_agent = CoverageAgent()

    def orchestrate(self, flow: str, feature_description: str) -> dict[str, str]:
        """Run the full multi-agent pipeline and return structured outputs."""
        gherkin = self.gherkin_agent.generate(flow, feature_description)
        script = self.script_agent.generate(gherkin)
        coverage = self.coverage_agent.analyze(feature_description, gherkin)

        return {
            "gherkin": gherkin,
            "script": script,
            "coverage": coverage,
        }
