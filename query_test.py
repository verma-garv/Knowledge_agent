import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("notes")

question = "Which free LLM API tiers does the sprint recommend?"
results = collection.query(query_texts=[question], n_results=3)
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(f"distance={dist:.3f}")
    print(doc[:300])
    print("---")
