import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator_agent import CoordinatorAgent
from agents.aggregator_agent import AggregatorAgent

coordinator = CoordinatorAgent()

aggregator = AggregatorAgent()

code = """
password = "123456"

for i in range(10000):
    for j in range(10000):
        print(i,j)
"""

results = coordinator.review_pull_request(code)

final_report = aggregator.aggregate(results)

print(final_report)
