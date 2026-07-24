"""Build the RAG knowledge base from data/knowledge_base/*.

Reads the collected agronomic documents (extension manuals, fertilizer guides,
crop calendars, soil/yield references), chunks them, embeds, and persists to a
local Chroma collection. Run via scripts/ingest_kb.py.
"""
from __future__ import annotations

import glob
import os

from app.config import settings

COLLECTION = "agrisense_kb"


def _chunk(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    """Naive char-based chunker. Swap for a sentence/heading-aware splitter."""
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest() -> int:
    """Ingest every file under KB_DIR into Chroma. Returns #chunks indexed.

    TODO:
      - import chromadb; client = chromadb.PersistentClient(settings.chroma_dir)
      - collection = client.get_or_create_collection(
            COLLECTION, embedding_function=get_embedding_function())
      - for each .md/.txt file: read, _chunk, add(ids, documents, metadatas)
      - metadatas should carry {"source": filename} for citation in the trace
    """
    files = glob.glob(os.path.join(settings.kb_dir, "**", "*"), recursive=True)
    files = [f for f in files if f.lower().endswith((".md", ".txt"))]
    if not files:
        print(f"[ingest] No .md/.txt files in {settings.kb_dir}. Add KB docs first.")
        return 0
    raise NotImplementedError("Wire Chroma persistent client + add chunks.")
