import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.testing_agent import TestingAgent

agent = TestingAgent()

code = """
def withdraw(amount):
    pass
"""

result = agent.review_code(code)

print(result)
