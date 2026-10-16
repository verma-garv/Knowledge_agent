import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("notes")

tests = [
    ("What percentages does the daily rhythm split time into?", "40% building"),
    ("Which free LLM API tiers does the sprint recommend?", "Google AI Studio"),
    ("What should you do on Day 10?", "cosine similarity"),
]
print(collection.metadata)

def rank_of_answer(question, must_contain, k=11):
    res = collection.query(query_texts=[question], n_results=k)
    for rank, doc in enumerate(res["documents"][0], start=1):
        if must_contain in doc:
            return rank
    return None

for q, needle in tests:
    print(rank_of_answer(q, needle), "<-", q)

print("chunks stored:", collection.count())
