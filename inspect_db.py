from collections import Counter

import chromadb

c = chromadb.PersistentClient(path="chroma_db").get_collection("notes")
print(c.count(), c.metadata)
data = c.get()
sizes = [len(d.split()) for d in data["documents"]]
print("words per chunk min/avg/max:", min(sizes), round(sum(sizes) / len(sizes)), max(sizes))
print(Counter(m["source"] for m in data["metadatas"]))
