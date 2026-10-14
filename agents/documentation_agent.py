from langchain_ollama import ChatOllama


class DocumentationAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_predict=256,
            reasoning=False,
        )

    def review_code(self, code):
        prompt = f"""
You are a senior software documentation engineer.

Review the supplied code for documentation issues:
1. Missing or unclear function and class docstrings
2. Undocumented parameters and return values
3. Unclear public interfaces
4. Misleading, outdated, or incorrect comments
5. Missing documentation for complex logic
6. Missing documentation for important assumptions

Rules:
- Prioritize documentation that would help another developer
  understand or safely use the code.
- Do not demand comments for obvious code.
- Do not report missing documentation for every simple line.
- Do not invent documentation problems.
- Avoid duplicate findings.
- Keep the response concise.

For each finding, use this format:

Severity: Critical, High, Medium, or Low
Issue: Explain the documentation problem and reference the code.
Recommendation: Describe the documentation that should be added
or corrected.

If no meaningful documentation issues exist, state that clearly.
Do not include internal reasoning.

CODE TO REVIEW:
{code}

Provide your findings directly.
"""

        response = self.llm.invoke(prompt)
        result = (response.content or "").strip()

        if not result:
            raise RuntimeError(
                "Documentation Agent received an empty response "
                "from Ollama. "
                f"Metadata: {response.response_metadata}"
            )

        return result
