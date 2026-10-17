import operator
import os
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, TypedDict

from tools import search_docs  # CHANGED: your tool, not add/multiply

load_dotenv()

provider = os.getenv("MODEL_PROVIDER", "groq")
if provider == "ollama":
    from langchain_ollama import ChatOllama
    model = ChatOllama(model="llama3.2:1b", temperature=0)
else:
    model = init_chat_model("openai/gpt-oss-120b", model_provider="groq", temperature=0)

tools = [search_docs]                  # tomorrow: add the web search tool here
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)

SYSTEM_PROMPT = """You are a study assistant for the user's own notes: the \
30-Day AI Engineer Sprint plan, covering the day-by-day schedule, projects, \
free resources, common beginner mistakes, and what to learn after Day 30.

You have one tool, search_docs, which searches those notes.

How to answer:
1. For any question about what the notes say or what the plan is, call \
search_docs first. Do not answer such questions from memory.
2. For general knowledge questions that have nothing to do with the notes, \
answer directly without calling the tool.
3. Each passage comes with a distance. A smaller distance means a closer \
match, but distance is only a hint. Read the passage itself and decide \
whether it actually answers the question. A passage with a large distance \
can still contain the answer, and a small distance does not guarantee it.
4. If the first search returns passages that don't answer the question, try \
once more with a differently worded query. After that, stop searching.
5. If the notes still don't answer it, say plainly that the notes don't \
cover it. Never invent details about the plan, and never present a guess \
as if it came from the notes.
6. When you use the notes, say which source file the answer came from. \
Keep answers short and in your own words rather than pasting long passages."""   # CHANGED: see the rules below


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def llm_node(state: AgentState):
    response = model_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )
    return {"messages": [response]}


def tool_node(state: AgentState):
    results = []
    for call in state["messages"][-1].tool_calls:
        t = tools_by_name[call["name"]]
        try:
            observation = t.invoke(call["args"])
        except Exception as e:
            observation = f"Error calling {call['name']}: {e}"
        results.append(ToolMessage(content=str(observation), tool_call_id=call["id"]))
    return {"messages": results}


def should_continue(state: AgentState) -> Literal["tool_node", END]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END


builder = StateGraph(AgentState)
builder.add_node("llm_node", llm_node)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_node")
builder.add_conditional_edges("llm_node", should_continue, ["tool_node", END])
builder.add_edge("tool_node", "llm_node")
agent = builder.compile()


if __name__ == "__main__":
    print(f"Using provider: {provider}")
    while True:
        question = input("\nAsk (or 'quit'): ").strip()
        if question.lower() == "quit":
            break
        result = agent.invoke(
            {"messages": [HumanMessage(content=question)]},
            config={"recursion_limit": 10},
        )
        for m in result["messages"]:
            m.pretty_print()
