import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator_agent import CoordinatorAgent

agent = CoordinatorAgent()

code = """
password = "123456"

for i in range(10000):
    for j in range(10000):
        print(i,j)
"""

result = agent.review_pull_request(code)

print(result)
