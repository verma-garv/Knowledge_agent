import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("notes")
print(collection.count(), collection.metadata)

answerable = [
    "What percentages does the daily rhythm split time into?",
    "Which free LLM API tiers does the sprint recommend?",
    "What should you do on Day 10?",
    "What should you do on Day 24?",
    "What are the mistakes that waste beginners' time?",
    "What is the capstone project?",
]
unanswerable = [
    "What is the capital of France?",
    "How do I bake sourdough bread?",
    "Who won the last football world cup?",
    "What is the boiling point of water?",
    "How do I change a car tire?",
]

def best_distance(q):
    res = collection.query(query_texts=[q], n_results=1)
    return res["distances"][0][0]

ans = [(best_distance(q), q) for q in answerable]
unans = [(best_distance(q), q) for q in unanswerable]

for d, q in sorted(ans + unans):
    label = "ANS  " if (d, q) in ans else "UNANS"
    print(label, round(d, 3), q)

worst_ans = max(d for d, _ in ans)
best_unans = min(d for d, _ in unans)
print("worst answerable:", round(worst_ans, 3))
print("best unanswerable:", round(best_unans, 3))
print("gap:", round(best_unans - worst_ans, 3))
