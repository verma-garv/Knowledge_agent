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

MAX_WORDS = 120
OVERLAP_LINES = 2          # lines, not words

chunks = chunk_lines(text, MAX_WORDS, OVERLAP_LINES)

sizes = [len(c.split()) for c in chunks]
print(f"{len(chunks)} chunks; words min/avg/max: "
      f"{min(sizes)}/{round(sum(sizes) / len(sizes))}/{max(sizes)}")
if sum(sizes) / len(sizes) > 1.5 * MAX_WORDS:
    raise ValueError("chunks are much larger than MAX_WORDS: check chunker arguments")

collection.upsert(
    documents=chunks,
    ids=[f"{path.name}-{i}" for i in range(len(chunks))],
    metadatas=[{"source": path.name} for _ in chunks],
)
print(len(chunks), "chunks stored; collection count:", collection.count())
