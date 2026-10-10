import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.bug_agent import BugAgent

agent = BugAgent()

code = """
def divide(a,b):
    return a/b
"""

result = agent.review_code(code)

print(result)
