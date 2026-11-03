import operator
import os
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, TypedDict

from tools import search_docs

load_dotenv()

MAX_SEARCHES = 2

provider = os.getenv("MODEL_PROVIDER", "groq")
if provider == "ollama":
    from langchain_ollama import ChatOllama
    model = ChatOllama(model="llama3.2:1b", temperature=0)
else:
    model = init_chat_model("openai/gpt-oss-120b", model_provider="groq", temperature=0)

tools = [search_docs]
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
4. If the first search doesn't answer the question, search once more using \
different content words. Repeating the same words with different punctuation \
does not count. After two searches, stop and answer.
5. If the search results still don't answer it, say plainly that the \
passages you found don't answer it. You have only seen part of the notes, so \
don't say the notes don't contain it. Suggest rephrasing with more specific \
topic words. Never invent details about the plan, and never present a guess \
as if it came from the notes.
6. When you use the notes, say which source file the answer came from. \
Keep answers short and in your own words rather than pasting long passages."""


FORCED_SYSTEM_PROMPT = """You answer questions about the user's own study notes, \
using only the passages retrieved from the notes.

Rules:
1. Use only the information in the passages. Do not use outside knowledge \
and do not guess.
2. Support your answer with one exact quote copied from the passages, in \
quotation marks.
3. If no passage answers the question, say plainly that the passages retrieved \
don't answer it, and that the answer may be in a part of the \
notes that wasn't retrieved. Suggest rephrasing with more specific topic \
words. Never claim the notes don't contain it, and never make up an answer. \
Say it this way: “The passages I retrieved don’t mention [the topic]. The answer may be in a part of the notes the search didn’t return.” Then suggest a rephrasing.
4. If you answer from the passages, name the source file the answer came from.
5. Keep the answer short and in your own words.
6. The passages come from an automatic search of the notes, \
not from the user. Refer to them as “the passages I retrieved” \
or “the search results”, \
never as passages the user provided."""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


def searches_this_turn(messages):
    """Count tool results since the user's latest question."""
    count = 0
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            break
        if isinstance(m, ToolMessage):
            count += 1
    return count


def question_and_passages(messages):
    """Return the latest user question and the search results gathered since it."""
    passages = []
    question = ""
    for m in reversed(messages):
        if isinstance(m, ToolMessage):
            passages.append(m.content)
        elif isinstance(m, HumanMessage):
            question = m.content
            break
    passages.reverse()
    return question, "\n".join(passages)


def llm_node(state: AgentState):
    if searches_this_turn(state["messages"]) >= MAX_SEARCHES:
        question, passages = question_and_passages(state["messages"])
        msgs = [
            SystemMessage(content=FORCED_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Question: {question}\n\n"
                f"Passages:\n{passages}\n\n"
                "Answer the question using only these passages."
            )),
        ]
        try:
            print(f"[forced answer: {len(passages.split())} words of passages]")
            response = model.invoke(msgs)
        except Exception as e:
            print(f"[final-answer call failed: {e}]")
            response = AIMessage(content=f"[error] final-answer call failed: {e}")
    else:
        msgs = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = model_with_tools.invoke(msgs)
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
        try:
            for step in agent.stream(
                {"messages": [HumanMessage(content=question)]},
                config={"recursion_limit": 10},
                stream_mode="values",
            ):
                step["messages"][-1].pretty_print()
        except GraphRecursionError:
            print("\n[stopped: hit the step limit without a final answer]")
