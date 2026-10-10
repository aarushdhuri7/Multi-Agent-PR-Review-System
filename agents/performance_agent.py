from langchain_ollama import ChatOllama


class PerformanceAgent:
    def __init__(self):

        self.llm = ChatOllama(model="qwen3:8b", temperature=0)

    def review_code(self, code):

        prompt = f"""
You are a performance optimization expert.

Review for:

1. Slow algorithms
2. Nested loops
3. Memory inefficiencies
4. Database bottlenecks
5. Scalability concerns

Return:

Severity:
Issue:
Recommendation:

Code:
{code}
"""

        response = self.llm.invoke(prompt)

        return response.content
