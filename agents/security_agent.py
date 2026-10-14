from langchain_ollama import ChatOllama


class SecurityAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_predict=256,
            reasoning=False,
        )

    def review_code(self, code):
        prompt = f"""
You are a senior cybersecurity engineer.

Review the code for:
1. SQL injection
2. Hardcoded secrets
3. Authentication flaws
4. Authorization flaws
5. API security issues

Return concise findings using this format:

Severity: Critical, High, Medium, or Low
Issue: Explain the vulnerability and cite relevant code.
Recommendation: Give a practical fix.

Do not invent vulnerabilities. If a category has no finding,
say so briefly. Avoid lengthy explanations and duplicate findings.

CODE TO REVIEW:
{code}

Provide your findings directly. Do not include internal reasoning.
"""
        response = self.llm.invoke(prompt)
        result = (response.content or "").strip()

        if not result:
            raise RuntimeError(
                "Security Agent received an empty response from Ollama. "
                f"Metadata: {response.response_metadata}"
            )

        return result
