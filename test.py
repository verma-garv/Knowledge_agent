from unittest.mock import patch

import httpx
from groq import BadRequestError
from langchain.messages import HumanMessage

import agent


class FakeModel:
    def __init__(self, error):
        self.error = error

    def invoke(self, msgs):
        raise self.error


q = {"messages": [HumanMessage(content="What is a router?")]}
bad = BadRequestError(
    "tool_use_failed",
    response=httpx.Response(400, request=httpx.Request("POST", "https://x")),
    body=None,
)

with patch.object(agent, "model_with_tools", FakeModel(bad)):
    print("1:", agent.agent.invoke(q)["messages"][-1].content[:80])

with patch.object(agent, "model_with_tools", FakeModel(ValueError("bug"))):
    try:
        agent.agent.invoke(q)
    except ValueError:
        print("2: ValueError was not swallowed")
