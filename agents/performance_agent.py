from langchain_ollama import ChatOllama


class PerformanceAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:8b",
            temperature=0,
            num_predict=256,
            reasoning=False,
        )

    def review_code(self, code):
        prompt = f"""
You are a senior software performance engineer.

Identify meaningful performance issues:
1. Inefficient loops or repeated work
2. Excessive database queries
3. Poor algorithmic complexity
4. Unnecessary memory usage
5. Blocking or inefficient I/O
6. Inefficient resource usage

For each finding, provide:
Severity: Critical, High, Medium, or Low
Issue: Explain the bottleneck and reference relevant code.
Recommendation: Give a practical optimization.

Avoid speculative micro-optimizations and duplicate findings.
Be concise. Do not invent performance problems.

CODE TO REVIEW:
{code}

Provide findings directly. Do not include internal reasoning.
"""
        response = self.llm.invoke(prompt)
        result = (response.content or "").strip()

        if not result:
            raise RuntimeError(
                "Performance Agent received an empty response from Ollama. "
                f"Metadata: {response.response_metadata}"
            )

        return result
