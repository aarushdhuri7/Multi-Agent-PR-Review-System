import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.performance_agent import PerformanceAgent

agent = PerformanceAgent()

code = """
for i in range(10000):
    for j in range(10000):
        print(i,j)
"""

result = agent.review_code(code)

print(result)
