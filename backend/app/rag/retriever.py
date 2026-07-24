"""Query the RAG knowledge base.

`search` is registered as an agent tool (search_knowledge_base) AND called
directly by the crop/season/fertilizer tools to ground their advice. Each hit
carries its source so the citation appears in the agent trace.
"""
from __future__ import annotations

from typing import Any

from app.config import settings
from app.rag.ingest import COLLECTION

_client = None
_collection = None


def _get_collection():
    """Lazily open the persistent Chroma collection."""
    global _client, _collection
    if _collection is not None:
        return _collection
    # TODO:
    # import chromadb
    # _client = chromadb.PersistentClient(path=settings.chroma_dir)
    # _collection = _client.get_collection(COLLECTION)
    # return _collection
    raise NotImplementedError("Open Chroma persistent collection.")


async def search(query: str, k: int = 4) -> list[dict[str, Any]]:
    """Return the top-k grounded snippets for a query.

    Shape: [{"text": "...", "source": "brri_rice_calendar.md", "score": 0.83}, ...]

    TODO: collection.query(query_texts=[query], n_results=k) and map results to
    the shape above (documents + metadatas + distances).
    """
    raise NotImplementedError
