import os

import chromadb
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("notes")

MAX_DISTANCE=1.82

@tool
def search_docs(query: str) -> str:
    """Search the user's own study notes:

    Use this for questions about what the notes say or what the plan is. Do not
    use it for general knowledge or for current information from the web.

    Args:
        query: A short phrase describing what to look up in the notes.
    """
    results = collection.query(query_texts=[query], n_results=4)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    ids = results["ids"][0]
    dis = results["distances"][0]

    parts = []
    for doc, meta, cid, dist in zip(docs, metas, ids, dis):
        parts.append(
            f"[source: {meta['source']} | chunk: {cid} | distance:{dist:.2f}]\n{doc}"
        )

    if not parts:
        return "No passages found in the notes."
    return "\n\n".join(parts)


load_dotenv()

MAX_RESULTS = 3
MAX_SNIPPET_CHARS = 500


@tool
def web_search(query: str) -> str:
    """Search the live web for current information or facts that are not in the
    user's notes, such as recent events, the latest version of a tool, or general
    knowledge.

    Do not use this for questions about the user's own study plan or notes. Use
    search_docs for those.

    Args:
        query: A short, specific search phrase, like one typed into a search engine.
    """
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query, max_results=MAX_RESULTS)
    except Exception as e:
        return f"Web search failed: {e}"

    results = response["results"]
    if not results:
        return "No web results found."

    parts = []
    for r in results:
        parts.append(f"[source: {r['url']} | title: {r['title']}]\n{r['content'][:MAX_SNIPPET_CHARS]}")
    return "\n\n".join(parts)

if __name__ == "__main__":
    print(search_docs.invoke({"query": "What should you do on Day 24?"}))
    print(web_search.invoke({"query": "What is the latest stable version of Python?"}))
