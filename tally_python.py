import time

from langchain.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from agent import agent

Q = "What is the latest stable version of Python?"
tally = {"has 3.15": 0, "no 3.15": 0, "error": 0}
for i in range(5):
    if i:
        time.sleep(30)
    try:
        ans = agent.invoke({"messages": [HumanMessage(content=Q)]},
                           config={"recursion_limit": 10})["messages"][-1].content
    except GraphRecursionError:
        tally["error"] += 1
        continue
    if ans.startswith("[error]"):
        tally["error"] += 1
    elif "3.15" in ans:
        tally["has 3.15"] += 1
    else:
        tally["no 3.15"] += 1
    print(i + 1, ans[:120].replace("\n", " "))
print(tally)
