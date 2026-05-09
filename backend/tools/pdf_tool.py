
# Pdf or Document Retriever
# Semantic search over ingested Pdf chunks using TF-IDF.
# No vector db , just lightweight and self-contained.

# We can swap embeddings for sentence-transformers later if needed.


import logging
import json
import math
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Where the processed chunks live (written by ingestion)
CHUNKS_PATH = Path(__file__).resolve().parent.parent / "db" / "pdf_chunks.json"

MAX_RESULTS = 5   # top-k cap


def _load_chunks() -> list[dict]:
    """Load pre-processed PDF chunks from disk."""
    if not CHUNKS_PATH.exists():
        log.warning("[pdf_tool] No chunks file found at %s — run ingestion first", CHUNKS_PATH)
        return []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into tokens."""
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _tfidf_score(query_tokens: list[str], chunk_tokens: list[str],
                 all_chunks: list[list[str]]) -> float:
    """
    Compute a simple TF-IDF dot-product score between query and chunk.
    Good enough for keyword-rich business documents.
    """
    N = len(all_chunks)
    score = 0.0

    for term in set(query_tokens):
        # TF in this chunk
        tf = chunk_tokens.count(term) / max(len(chunk_tokens), 1)
        # IDF across all chunks
        df = sum(1 for c in all_chunks if term in c)
        idf = math.log((N + 1) / (df + 1)) + 1
        score += tf * idf

    return round(score, 4)


def search_documents(query: str, top_k: int = 3) -> dict[str, Any]:
    # main func called by orchestrator
    log.info("[pdf_tool] Search query: '%s' top_k=%d", query, top_k)

    top_k = min(top_k, MAX_RESULTS)

    chunks = _load_chunks()
    if not chunks:
        return {
            "success": False,
            "results": [],
            "result_count": 0,
            "error": "No documents ingested. Run POST /ingest first.",
        }

    query_tokens = _tokenize(query)
    if not query_tokens:
        return {
            "success": False,
            "results": [],
            "result_count": 0,
            "error": "Query produced no searchable tokens.",
        }

    # Tokenize all chunks once
    tokenized_chunks = [_tokenize(c["text"]) for c in chunks]

    # Score every chunk
    scored = [
        (i, _tfidf_score(query_tokens, tokenized_chunks[i], tokenized_chunks))
        for i in range(len(chunks))
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in scored[:top_k]:
        if score == 0:
            break   # if there is no relevance at all — stop early
        chunk = chunks[idx]
        results.append({
            "source":      chunk.get("source", "unknown"),
            "page":        chunk.get("page", 0),
            "chunk_index": chunk.get("chunk_index", idx),
            "text":        chunk["text"],
            "score":       score,
        })

    log.info("[pdf_tool] Returning %d results for query '%s'", len(results), query)
    return {
        "success":      True,
        "results":      results,
        "result_count": len(results),
        "error":        None,
    }