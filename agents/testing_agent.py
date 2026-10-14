from langchain_ollama import ChatOllama


class TestingAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_predict=256,
            reasoning=False,
        )

    def review_code(self, code):
        prompt = f"""
You are a senior software test engineer.

Review the supplied code for testing weaknesses:
1. Missing tests for important functions
2. Missing edge-case tests
3. Weak or missing assertions
4. Missing error-handling tests
5. Missing tests for invalid inputs
6. Missing tests for important failure scenarios

Rules:
- Focus on meaningful gaps in test coverage.
- Do not claim tests are missing if the supplied code
  already includes adequate tests.
- If no tests are provided, identify important test cases
  that should be added.
- Do not invent defects or duplicate findings.
- Keep the response concise.

For each finding, use this format:

Severity: Critical, High, Medium, or Low
Issue: Explain the testing gap and reference relevant code.
Recommendation: Describe the test that should be added.

If no meaningful testing issues exist, state that clearly.
Do not include internal reasoning.

CODE TO REVIEW:
{code}

Provide your findings directly.
"""

        response = self.llm.invoke(prompt)
        result = (response.content or "").strip()

        if not result:
            raise RuntimeError(
                "Testing Agent received an empty response from Ollama. "
                f"Metadata: {response.response_metadata}"
            )

        return result
