from langchain_ollama import ChatOllama


class DocumentationAgent:
    def __init__(self):

        self.llm = ChatOllama(model="qwen3:8b", temperature=0)

    def review_code(self, code):

        prompt = f"""
You are a software documentation expert.

Check:

1. Missing comments
2. Missing docstrings
3. Missing API documentation
4. Poor readability
5. Maintainability concerns

Return:

Severity:
Issue:
Recommendation:

Code:
{code}
"""

        response = self.llm.invoke(prompt)

        return response.content
