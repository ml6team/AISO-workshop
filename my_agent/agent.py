"""
This file is where you will implement your agent.
The `run_agent` function is used to evaluate your agent's performance.
"""

from google.adk.agents.llm_agent import Agent
from .tools.web_search import web_search

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agent',
    description="A helpful assistant that can answer questions.",
    instruction="You are a helpful assistant that answers questions directly and concisely.",
    tools=[web_search],
)
