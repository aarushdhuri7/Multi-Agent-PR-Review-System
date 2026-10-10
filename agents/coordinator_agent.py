from agents.security_agent import SecurityAgent
from agents.bug_agent import BugAgent
from agents.performance_agent import PerformanceAgent
from agents.testing_agent import TestingAgent
from agents.documentation_agent import DocumentationAgent


class CoordinatorAgent:
    def __init__(self):
        self.security = SecurityAgent()
        self.bug = BugAgent()
        self.performance = PerformanceAgent()
        self.testing = TestingAgent()
        self.documentation = DocumentationAgent()

    def review_pull_request(self, code):
        print("\n" + "=" * 60)
        print("COORDINATOR AGENT STARTED")
        print("=" * 60)

        agents = [
            ("security", "Security", self.security),
            ("bug", "Bug", self.bug),
            ("performance", "Performance", self.performance),
            ("testing", "Testing", self.testing),
            ("documentation", "Documentation", self.documentation),
        ]

        results = {}
        failures = []

        for index, (key, name, agent) in enumerate(agents, start=1):
            print(f"\n[{index}/5] Running {name} Agent...")

            try:
                result = agent.review_code(code)

                if result is None or result == "":
                    raise ValueError("Agent returned an empty result.")

                results[key] = result
                print(f"✓ {name} Review Completed")

            except Exception as exc:
                print(f"✗ {name} Agent Failed: {exc}")

                results[key] = {
                    "status": "error",
                    "message": str(exc),
                }
                failures.append(name)

        print("\n" + "=" * 60)

        if failures:
            print("COORDINATOR FINISHED WITH ERRORS")
            print("Failed agents: " + ", ".join(failures))
        else:
            print("ALL FIVE AGENTS COMPLETED SUCCESSFULLY")

        print("=" * 60)

        return results
