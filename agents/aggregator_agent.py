class AggregatorAgent:
    """Combine specialist-agent findings without another LLM call."""

    def aggregate(self, findings):
        print("\nAGGREGATOR STARTED", flush=True)

        if not isinstance(findings, dict):
            raise ValueError("Expected agent findings as a dictionary.")

        sections = {
            "security": "SECURITY REVIEW",
            "bug": "BUG REVIEW",
            "performance": "PERFORMANCE REVIEW",
            "testing": "TESTING RECOMMENDATIONS",
            "documentation": "DOCUMENTATION REVIEW",
        }

        report = [
            "PULL REQUEST REVIEW SUMMARY",
            "=" * 40,
            "Results from specialist code-review agents.",
            "",
        ]

        failed_agents = []
        successful_count = 0

        for agent_name, result in findings.items():
            name = agent_name.lower()

            # Detect explicit agent failures
            if isinstance(result, dict) and result.get("status") == "error":
                failed_agents.append(
                    f"{agent_name}: {result.get('message', 'Unknown agent error')}"
                )
                continue

            if result is None or (isinstance(result, str) and not result.strip()):
                failed_agents.append(f"{agent_name}: Empty result returned.")
                continue

            if isinstance(result, str) and "agent error" in result.lower():
                failed_agents.append(f"{agent_name}: {result}")
                continue

            heading = sections.get(
                name,
                f"{agent_name.replace('_', ' ').upper()} REVIEW",
            )

            report.extend(
                [
                    heading,
                    "-" * len(heading),
                    str(result).strip(),
                    "",
                ]
            )
            successful_count += 1

        report.extend(
            [
                "FINAL RECOMMENDATION",
                "-" * 20,
            ]
        )

        if failed_agents:
            report.extend(
                [
                    "Manual review is recommended because one or more agents failed.",
                    "",
                    "AGENT ERRORS",
                ]
            )
            for error in failed_agents:
                report.append(f"- {error}")

        elif successful_count:
            report.append(
                "Review the findings above, verify reported issues, "
                "and run appropriate tests before merging."
            )

        else:
            report.append(
                "No usable findings were returned. Manual review is required."
            )

        print("AGGREGATOR COMPLETED", flush=True)
        return "\n".join(report)
