"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent
from my_agent.tools import web_search
from my_agent.tools import calculator
from my_agent.tools import pdf_extract

root_agent = llm_agent.Agent(
    model='gemini-2.5-flash-lite',
    name='agent',
    description="A helpful assistant that can answer questions.",
    instruction="You are a helpful assistant that answers questions directly and concisely.",
    tools=[web_search, calculator, pdf_extract],
    sub_agents=[],
)
