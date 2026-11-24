import time

from langchain.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from agent import agent, provider

CASES = [
    # (question, keywords that must all appear, should the tool be called?, known-failure reason or None)
    ("What is routing", ["routing"], True, None)
    ("What is the capital of France?", ["paris"], False, None),
    ("What is the latest stable version of Python?", ["3.15"], True, None),
]


def used_tool(messages):
    return any(getattr(m, "tool_calls", None) for m in messages)


PAUSE = 30   # seconds between questions, to stay under the per-minute token limit


def normalize(s):
    for ch in ("\u2011", "\u2010", "\u2013", "\u2014"):
        s = s.replace(ch, "-")
    s = s.replace("\u00a0", " ").replace("\u202f", " ").replace(" %", "%")
    return s.lower()


def used_tool(messages):
    return any(getattr(m, "tool_calls", None) for m in messages)


counts = {"passed": 0, "failed": 0, "known": 0, "unexpected_pass": 0, "error": 0}
print(f"Provider: {provider}\n")

for i, (question, keywords, expect_tool, known_reason) in enumerate(CASES):
    if i > 0:
        time.sleep(PAUSE)          # waits before every question except the first

    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=question)]},
            config={"recursion_limit": 10},
        )
    except GraphRecursionError:
        print("FAIL (hit step limit) <-", question)
        counts["failed"] += 1
        continue

    answer = result["messages"][-1].content

    if answer.startswith("[error]"):
        print("ERROR <-", question)
        counts["error"] += 1
        continue

    keywords_ok = all(normalize(k) in normalize(answer) for k in keywords)
    tool_ok = used_tool(result["messages"]) == expect_tool
    ok = keywords_ok and tool_ok

    if ok and known_reason is None:
        print("PASS <-", question)
        counts["passed"] += 1
    elif ok:
        print("UNEXPECTED PASS (remove the known-failure mark) <-", question)
        counts["unexpected_pass"] += 1
    elif known_reason is not None:
        print("KNOWN FAILURE <-", question)
        print("   reason:", known_reason)
        counts["known"] += 1
    else:
        print("FAIL <-", question)
        print("   keywords found:", keywords_ok, "| tool use as expected:", tool_ok)
        print("   answer:", answer[:200])
        counts["failed"] += 1

# your turn: print one summary line that reports every count in `counts`
print(f"No. of pass {counts["passed"]}\nNo. of failed {counts["failed"]}\nNo. of known {counts["known"]}\nNo. of unexpected_pass {counts["unexpected_pass"]}\nNo. of error {counts["error"]}")
