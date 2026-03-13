"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.
"""

from google.adk.agents import llm_agent

from my_agent.tools import calculator

root_agent = llm_agent.Agent(
    model="gemini-2.5-flash-lite",
    name="agent",
    description="A helpful assistant that can answer questions.",
    instruction=(
        "You are a helpful assistant that answers "
        "questions directly and concisely. "
        "Use the calculator tool for all arithmetic."
    ),
    tools=[calculator],
    sub_agents=[],
)
