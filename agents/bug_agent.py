from langchain_ollama import ChatOllama


class BugAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_predict=256,
            reasoning=False,
        )

    def review_code(self, code):
        prompt = f"""Find up to 2 genuine bugs in this code:
{code}

Return concise results in this format:
Severity: High/Medium/Low
Issue: Explain the bug.
Recommendation: Explain the fix.

If there are no clear bugs, say "No clear bugs found."
Do not include reasoning or repeat findings.
"""

        response = self.llm.invoke(prompt)
        result = (response.content or "").strip()

        if not result:
            raise RuntimeError(
                "Bug Agent received an empty response from Ollama. "
                f"Metadata: {response.response_metadata}"
            )

        return result
