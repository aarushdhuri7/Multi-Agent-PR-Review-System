from langchain_ollama import ChatOllama


class SecurityAgent:
    def __init__(self):

        self.llm = ChatOllama(model="qwen3:8b", temperature=0)

    def review_code(self, code):

        prompt = f"""
You are a senior cybersecurity engineer.

Review the following code.

Identify:

1. SQL Injection
2. Hardcoded secrets
3. Authentication flaws
4. Authorization flaws
5. API security issues

Return findings in this format:

Severity:
Issue:
Recommendation:

Code:
{code}
"""

        response = self.llm.invoke(prompt)

        return response.content
