import time

from langchain.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from agent import agent, provider

# (question, phrase the answer must contain, should the agent call the tool?)
CASES = [
    ("What should you do on Day 24?", "fastapi", True),
    ("What percentages does the daily rhythm split time into?", "40%", True),
    ("Which free LLM API tiers does the sprint recommend?", "groq", True),
    ("What does the sprint say about Kubernetes?", "day 30", True),
    ("What is the capital of France?", "paris", False),
]


def used_tool(messages):
    return any(getattr(m, "tool_calls", None) for m in messages)


passed = 0
print(f"Provider: {provider}\n")

for question, phrase, expect_tool in CASES:
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=question)]},
            config={"recursion_limit": 10},
        )
    except GraphRecursionError:
        print("FAIL (hit step limit) <-", question)
        continue

    answer = result["messages"][-1].content
    phrase_ok = phrase in answer.lower()
    tool_ok = used_tool(result["messages"]) == expect_tool
    ok = phrase_ok and tool_ok
    passed += ok

    if answer.startswith("[error]"):
        print("ERROR <-", question)
        continue
    print("PASS" if ok else "FAIL", "<-", question)
    if not ok:
        print("   phrase found:", phrase_ok, "| tool use as expected:", tool_ok)
        print("   answer:", answer[:200])
    time.sleep(30)

print(f"\n{passed}/{len(CASES)} passed")
