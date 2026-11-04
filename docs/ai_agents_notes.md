# AI Agents and Agentic AI: Study Notes

These notes cover the core ideas behind agents built on large language models (LLMs). They are written for beginners who want a map of the territory before building anything.

## 1. What is an AI agent
- An AI agent is a system where a language model decides what to do next, uses tools to act on the world, and repeats until a task is done.
- Agentic AI is the broader term for systems that show this kind of autonomy: setting sub-goals, choosing actions, and adapting to feedback.
- A plain chatbot answers one message at a time. An agent can take many steps before it replies.
- The key difference is control: in an agent the model decides the path, and in a workflow the code decides it.

## 2. Workflows vs agents
- A workflow connects LLM calls and tools along a path that the developer wrote in advance.
- An agent chooses its own steps and tools at run time. The developer sets the goal, the tools, and the limits.
- Workflows are cheaper, faster and more predictable. Agents are more flexible, but slower, costlier, and harder to test.
- Rule of thumb: start with the simplest thing that works. Try a single LLM call first, then a workflow, and use an agent only when the steps cannot be known in advance.

## 3. Five common workflow patterns

| Pattern | What it does | Use it when |
|---|---|---|
| Prompt chaining | Splits a task into steps, each LLM call feeding the next | The task breaks into clean sequential subtasks |
| Routing | Classifies the input and sends it to a specialised handler | Different kinds of input need different treatment |
| Parallelization | Runs subtasks at the same time, or runs one task several times and compares | Speed matters, or you want several independent opinions |
| Orchestrator-workers | A central model breaks the task down and delegates to worker models | The subtasks cannot be predicted in advance |
| Evaluator-optimizer | One model produces an answer, another critiques it, and the loop repeats | There are clear quality criteria and revision helps |

## 4. The agent loop
1. The agent receives a goal from the user.
2. The model decides: answer directly, or call a tool.
3. The program runs the tool and captures the result.
4. The result is added to the conversation as an observation.
5. The model reads the updated context and decides again.
6. The loop ends when the model gives a final answer, or when a stopping condition triggers.
- Stopping conditions include a maximum number of steps, a token or cost budget, a timeout, and a human approval step.
- Without a stopping condition, an agent can repeat the same failing action forever.
- Ground truth from the environment, such as a tool result or a test outcome, is what lets an agent check its own progress.

## 5. Tools
- A tool is a function the model can ask the program to run. It is described by a name, a description, and a schema for its arguments.
- The model never runs code itself. It outputs a structured request, and the program executes it.
- Common tools are web search, a calculator, file reading, database queries, code execution, and calls to other APIs.
- Tool descriptions matter as much as prompts. A vague name or description makes the model pick the wrong tool or pass bad arguments.
- Design tips: use clear names, keep arguments few and simple, state in the description when to use the tool and when not to, and return helpful error messages as text.
- Make mistakes hard to make. If a tool takes a file path, requiring absolute paths removes a whole class of errors.

## 6. Memory and context
- The model has no memory between calls. Everything it knows about the conversation is what the program sends each time.
- Short-term memory is the message list for the current task. It grows with every step and is limited by the context window.
- Long-term memory is information stored outside the model, such as in a database or vector store, and retrieved when needed.
- Context is a budget. Long tool outputs use it up quickly, so trim results, summarise old turns, or store only the final answers.
- Hosted APIs also limit tokens per minute, so a large request can be rejected even when it fits inside the context window.

## 7. Retrieval-augmented generation (RAG)
- RAG gives the model relevant text from your own documents at question time, instead of relying only on what it learned in training.
- The steps are: split documents into chunks, embed each chunk as a vector, store the vectors, embed the question, retrieve the nearest chunks, and put them in the prompt.
- An embedding is a list of numbers that places texts with similar meanings close together.
- Chunk size is a trade-off. Large chunks dilute a single fact, and very small chunks lose context. Overlap keeps sentences from being cut apart.
- Embedding search ranks by similarity of meaning, so it is weak at exact labels and numbers. Hybrid search adds keyword matching to cover that gap.
- A retriever always returns its top results, even when none of them is relevant, so a system should check relevance before trusting them.
- In an agent, retrieval is usually a tool the model chooses to call, not a step that always runs.

## 8. MCP (Model Context Protocol)
- MCP is an open protocol for connecting AI applications to tools and data sources in a standard way.
- An MCP server exposes tools. An MCP client, which lives inside the application, discovers and calls them.
- Local servers often communicate over standard input and output. Remote servers use HTTP-based transports.
- The benefit is reuse: one server can work with many clients, instead of every application wiring up each tool by hand.
- MCP standardises how tools are described and called, but the model's own tool-call format still differs between providers.

## 9. Evaluation and testing
- Agent behaviour varies from run to run, so one successful run proves little. Run important cases several times.
- Keep a small set of questions with known answers and rerun it after every change. This is a regression test.
- Check behaviour as well as content: did the agent call the right tool, and did it stop on time?
- Keyword checks are simple, but they cannot tell "do this" from "do not do this". An LLM judge reads for meaning, but it adds cost and can be wrong too.
- Separate infrastructure errors, such as rate limits, from wrong answers, so a failing API is not mistaken for a bad agent.
- Mark known failures with their cause, so new failures stand out.
- Tracing, which means logging each model call, tool call and result, is the most useful debugging tool.

## 10. Common failure modes
1. Looping: repeating the same tool call with slightly different wording.
2. Wrong tool: choosing a tool that does not fit the question.
3. Invalid arguments: calling a tool with fields that do not exist.
4. Stale information: trusting an old web page for a question about the latest state of something.
5. Overclaiming: saying that something does not exist when the search simply missed it.
6. Hallucinated citations: naming a source that does not say what the answer claims.
7. Prompt injection: following instructions hidden in a web page or document the agent read.
8. Context overflow: running out of context or token budget partway through a task.

## 11. Guardrails and safety
- Treat everything a tool returns as data to read, never as instructions to follow.
- Give agents the fewest permissions that let them do the job.
- Require human approval for actions that are hard to undo, such as sending messages, spending money, or deleting data.
- Run agents that execute code inside a sandbox.
- Set hard limits in code: step counts, budgets and timeouts. A rule in a prompt is a request, and a check in code is enforcement.
- Log what the agent did so a person can review it.

## 12. Frameworks
- A framework can speed up the start. LangGraph and CrewAI are two well-known examples.
- LangGraph models an agent as a graph: nodes are functions, and edges decide which node runs next.
- Frameworks add layers that can hide what the prompts and tool calls actually are. Build the loop by hand once, so you can tell what a framework does for you.
- Reduce abstraction as a project moves toward production.

## 13. Cost, latency and model choice
- Each step in an agent loop is a model call, so cost and latency grow with the number of steps.
- Larger models follow instructions and format tool calls more reliably. Small local models are cheap and private, but they often fail at tool calling.
- Reasoning models spend extra tokens thinking before they answer, and those tokens count against output limits.
- Quantization stores a model's weights at lower precision, such as 8-bit or 4-bit. This cuts memory use and lets small models run on a CPU, at some cost in quality.

## 14. Glossary

| Term | Meaning |
|---|---|
| Agent | A system in which a model chooses actions, runs tools, and loops until a task is done |
| Tool call | A structured request from the model asking the program to run a function |
| Observation | The result of a tool call, added back into the conversation |
| Context window | The maximum amount of text a model can read in one call |
| Embedding | A vector of numbers that represents the meaning of a piece of text |
| Chunk | A piece of a document, sized for retrieval |
| Top-k | The number of nearest chunks a retriever returns |
| Hallucination | A confident statement that is not supported by facts or sources |
| Guardrail | A limit or check that keeps an agent within safe behaviour |
