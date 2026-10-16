import chromadb
from pathlib import Path


def chunk_text(text, size, overlap):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    words = text.split()
    chunks = []
    step = size - overlap
    start = 0
    while start < len(words):
        chunk = words[start: start + size]
        chunks.append(" ".join(chunk))
        if start + size >= len(words):
            break
        start += step
    return chunks


client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("notes")

path = Path("Docs/30_Day_AI_Engineer_Sprint (1).md")
text = path.read_text(encoding="utf-8")
print(len(text.split()), "words")

chunks = chunk_text(text, 200, 40)

collection.upsert(
    documents=chunks,
    ids=[f"{path.name}-{i}" for i in range(len(chunks))],
    metadatas=[{"source": path.name} for _ in chunks],
)
print(len(chunks), "chunks stored; collection count:", collection.count())
