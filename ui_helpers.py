from langchain.messages import ToolMessage


def describe_steps(messages):
    """Turn the agent's tool calls and results into short display lines."""
    lines = []
    for m in messages:
        if getattr(m, "tool_calls", None):
            for call in m.tool_calls:
                lines.append(f"Called {call['name']} with: {call['args']}")
        elif isinstance(m, ToolMessage):
            preview = " ".join(m.content.split())[:300]
            lines.append(f"Result: {preview}")
    return lines
