import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.documentation_agent import DocumentationAgent

agent = DocumentationAgent()

code = """
def calc(x,y):
    return x*y
"""

result = agent.review_code(code)

print(result)
