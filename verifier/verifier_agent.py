import re


class VerifierAgent:
    """Validate agent outputs using lightweight, deterministic checks."""

    def verify(self, findings):
        if not isinstance(findings, dict):
            raise ValueError("Findings must be a dictionary.")

        verified_findings = {}
        agent_errors = []
        validation_warnings = []
        duplicate_findings = []
        checks_performed = 0
        seen_lines = {}

        severity_pattern = re.compile(
            r"\b(critical|high|medium|low|info|informational)\b",
            re.IGNORECASE,
        )

        evidence_pattern = re.compile(
            r"\b(line\s*\d+|`[^`]+`|function|method|"
            r"variable|code|because|when|if)\b",
            re.IGNORECASE,
        )

        for agent_name, result in findings.items():
            checks_performed += 1

            if isinstance(result, dict) and result.get("status") == "error":
                agent_errors.append(
                    {
                        "agent": agent_name,
                        "message": result.get("message", "Agent failed."),
                    }
                )
                continue

            if result is None or not str(result).strip():
                agent_errors.append(
                    {
                        "agent": agent_name,
                        "message": "Agent returned an empty result.",
                    }
                )
                continue

            if isinstance(result, str) and "agent error" in result.lower():
                agent_errors.append(
                    {
                        "agent": agent_name,
                        "message": result,
                    }
                )
                continue

            text = str(result).strip()
            verified_findings[agent_name] = result

            # Check whether severity labels are present.
            if not severity_pattern.search(text):
                validation_warnings.append(
                    {
                        "agent": agent_name,
                        "check": "severity",
                        "message": "No explicit severity label detected.",
                    }
                )

            # Heuristic only: look for references to code or reasoning.
            if not evidence_pattern.search(text):
                validation_warnings.append(
                    {
                        "agent": agent_name,
                        "check": "evidence",
                        "message": "No obvious code reference or reasoning detected.",
                    }
                )

            # Detect identical non-trivial lines across agent outputs.
            for line in text.splitlines():
                normalized = re.sub(r"\s+", " ", line).strip().lower()

                if len(normalized) < 25:
                    continue

                if normalized in seen_lines:
                    previous_agent = seen_lines[normalized]
                    if previous_agent != agent_name:
                        duplicate_findings.append(
                            {
                                "agents": [previous_agent, agent_name],
                                "text": line.strip(),
                            }
                        )
                else:
                    seen_lines[normalized] = agent_name

        complete = len(agent_errors) == 0

        if not complete:
            status = "issues_detected"
        elif validation_warnings or duplicate_findings:
            status = "passed_with_warnings"
        else:
            status = "passed"

        message = (
            f"Verifier checked {checks_performed} agent outputs: "
            f"{len(verified_findings)} usable, "
            f"{len(agent_errors)} errors, "
            f"{len(validation_warnings)} warnings, "
            f"{len(duplicate_findings)} possible duplicates."
        )

        return {
            "findings": verified_findings,
            "agent_errors": agent_errors,
            "complete": complete,
            "status": status,
            "status_message": message,
            "checks_performed": checks_performed,
            "validation_warnings": validation_warnings,
            "duplicate_findings": duplicate_findings,
        }
