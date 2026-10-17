import chromadb
from langchain.tools import tool

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("notes")

MAX_DISTANCE=1.815

@tool
def search_docs(query: str) -> str:
    """Search the user's own study notes: the 30-Day AI Engineer Sprint plan,
    including the day-by-day schedule, projects, free resources, common beginner
    mistakes, and what to learn after Day 30.

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


print(search_docs.invoke({"query": "What percentages does the daily rhythm split time into?"}))
