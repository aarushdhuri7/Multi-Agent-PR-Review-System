import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.security_agent import SecurityAgent

agent = SecurityAgent()

code = """
query = f"SELECT * FROM users WHERE username='{user}'"
"""

result = agent.review_code(code)

print(result)
