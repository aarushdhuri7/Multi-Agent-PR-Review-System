from langchain_ollama import ChatOllama


class BugAgent:
    def __init__(self):

        self.llm = ChatOllama(model="qwen3:8b", temperature=0)

    def review_code(self, code):

        prompt = f"""
You are a senior software engineer.

Review the code for:

1. Logic errors
2. Edge cases
3. Runtime exceptions
4. Incorrect conditions
5. Functional bugs

Return findings in this format:

Severity:
Issue:
Recommendation:

Code:
{code}
"""

        response = self.llm.invoke(prompt)

        return response.content
