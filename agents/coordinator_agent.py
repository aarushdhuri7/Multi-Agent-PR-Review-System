from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

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
        print("\n" + "=" * 60, flush=True)
        print("COORDINATOR AGENT STARTED", flush=True)
        print("=" * 60, flush=True)

        agents = {
            "security": self.security,
            "bug": self.bug,
            "performance": self.performance,
            "testing": self.testing,
            "documentation": self.documentation,
        }

        results = {}
        overall_start = perf_counter()

        def run_agent(name, agent):
            start = perf_counter()

            try:
                result = agent.review_code(code)

                if result is None or (isinstance(result, str) and not result.strip()):
                    return (
                        name,
                        None,
                        perf_counter() - start,
                        "Agent returned an empty result.",
                    )

                return name, result, perf_counter() - start, None

            except Exception as exc:
                return name, None, perf_counter() - start, str(exc)

        # Start all five independent agents concurrently.
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(run_agent, name, agent): name
                for name, agent in agents.items()
            }

            for future in as_completed(futures):
                name, result, elapsed, error = future.result()

                if error:
                    print(
                        f"[FAILED] {name}: {error} ({elapsed:.1f}s)",
                        flush=True,
                    )
                    results[name] = {
                        "status": "error",
                        "message": error,
                    }
                else:
                    print(
                        f"[COMPLETED] {name}: {elapsed:.1f}s",
                        flush=True,
                    )
                    results[name] = result

        total_time = perf_counter() - overall_start

        print("-" * 60, flush=True)
        print(
            f"ALL FIVE AGENTS FINISHED IN {total_time:.1f}s",
            flush=True,
        )
        print("=" * 60, flush=True)

        # Preserve a predictable order in the returned dictionary.
        return {name: results[name] for name in agents}
