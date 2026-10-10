from langchain_ollama import ChatOllama


class TestingAgent:
    def __init__(self):

        self.llm = ChatOllama(model="qwen3:8b", temperature=0)

    def review_code(self, code):

        prompt = f"""
You are a QA engineer.

Review the code and identify:

1. Missing test cases
2. Missing edge case testing
3. Coverage gaps
4. Untested scenarios

Return:

Severity:
Issue:
Recommendation:

Code:
{code}
"""

        response = self.llm.invoke(prompt)

        return response.content
