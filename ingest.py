from pathlib import Path

import chromadb


def chunk_lines(text, max_words=120, overlap_lines=2):
    lines = [l for l in text.splitlines() if l.strip()]
    chunks = []
    current = []
    count = 0
    for line in lines:
        n = len(line.split())
        if current and count + n > max_words:
            chunks.append("\n".join(current))
            current = current[-overlap_lines:]          # carry the last lines over
            count = sum(len(l.split()) for l in current)
        current.append(line)
        count += n
    if current:
        chunks.append("\n".join(current))
    return chunks

SIZE = 120
OVERLAP = 30

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    "notes", metadata={"chunk_size": SIZE, "overlap": OVERLAP}
)

path = Path("Docs/30_Day_AI_Engineer_Sprint.md")
text = path.read_text(encoding="utf-8")
print(len(text.split()), "words")

chunks = chunk_lines(text, SIZE, OVERLAP)

collection.upsert(
    documents=chunks,
    ids=[f"{path.name}-{i}" for i in range(len(chunks))],
    metadatas=[{"source": path.name} for _ in chunks],
)
print(len(chunks), "chunks stored; collection count:", collection.count())
