"""Local knowledge retrieval using a lightweight vector store over repository docs."""

from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge"


def load_knowledge_documents(folder: Path) -> list[str]:
    documents: list[str] = []
    if not folder.exists():
        return documents

    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if text.strip():
                documents.append(text.strip())
    return documents


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) < max_chars:
            current = f"{current}\n\n{paragraph}" if current else paragraph
        else:
            if current:
                chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


class SimpleVectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.chunks: list[str] = []
        self.vectors: np.ndarray | None = None

    def add_texts(self, texts: list[str]) -> None:
        self.chunks = texts
        self.vectors = self.embedder.encode(texts, normalize_embeddings=True)

    def similarity_search(self, query: str, k: int = 3) -> list[str]:
        if not self.chunks or self.vectors is None:
            return []

        query_vec = self.embedder.encode([query], normalize_embeddings=True)[0]
        scores = self.vectors @ query_vec
        top_k = np.argsort(scores)[::-1][:k]
        return [self.chunks[i] for i in top_k]


embedder = SentenceTransformer("all-MiniLM-L6-v2")
vector_store = SimpleVectorStore(embedder)

knowledge_documents = load_knowledge_documents(KNOWLEDGE_DIR)
knowledge_chunks: list[str] = []
for document in knowledge_documents:
    knowledge_chunks.extend(chunk_text(document))

if knowledge_chunks:
    vector_store.add_texts(knowledge_chunks)


def search_local(query: str, k: int = 3) -> list[str]:
    """Return the most relevant knowledge chunks for a query."""
    return vector_store.similarity_search(query, k=k)