"""
Build Granite Embedding Index

Reads parsed standards markdown files from standards/parsed/ and builds
a semantic search index using sentence-transformers (Granite Embedding).

Output: standards/index/chunks.json — array of {id, text, source_document,
standard_body, section, embedding} objects.

This index is COMMITTED to the repository. It is never rebuilt at request time.

Usage:
    cd backend
    python scripts/build_index.py
"""
from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).parent.parent
PARSED_DIR = BACKEND_ROOT / "standards" / "parsed"
INDEX_DIR = BACKEND_ROOT / "standards" / "index"
INDEX_FILE = INDEX_DIR / "chunks.json"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Chunk settings
CHUNK_SIZE = 400        # words per chunk
CHUNK_OVERLAP = 50      # words overlap between chunks
MIN_CHUNK_WORDS = 20    # minimum words to keep a chunk

# Document → regulatory body mapping
_BODY_MAP = {
    "fcc": "FCC",
    "iadc": "IADC",
    "iso_24113": "ISO",
    "esa_zero_debris": "ESA",
    "copuos": "COPUOS",
}


def _get_body_from_filename(filename: str) -> str:
    filename_lower = filename.lower()
    for key, body in _BODY_MAP.items():
        if key in filename_lower:
            return body
    return "UNKNOWN"


def _split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        if len(chunk_words) >= MIN_CHUNK_WORDS:
            chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def _extract_section(text: str) -> str:
    """Try to extract the section identifier from chunk text."""
    match = re.search(r"(Section\s+[\d.]+|§\s*[\d.]+|\bClause\s+[\d.]+)", text[:200], re.IGNORECASE)
    if match:
        return match.group(0)
    return ""


def build_index_with_embeddings() -> list[dict]:
    """Build the embedding index with actual embeddings if model available."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("ibm-granite/granite-embedding-30m-english")
        logger.info("Using Granite Embedding model for index building")
        use_embeddings = True
    except Exception as exc:
        logger.warning("Embedding model not available: %s. Building text-only index.", exc)
        use_embeddings = False
        model = None

    parsed_files = list(PARSED_DIR.glob("*.md"))
    if not parsed_files:
        logger.warning("No parsed documents found in %s", PARSED_DIR)
        return []

    all_chunks = []
    chunk_id = 0

    for doc_path in sorted(parsed_files):
        body = _get_body_from_filename(doc_path.stem)
        text = doc_path.read_text(encoding="utf-8")
        chunks = _split_into_chunks(text)

        logger.info("Processing %s (%d words → %d chunks)", doc_path.name, len(text.split()), len(chunks))

        for chunk_text in chunks:
            section = _extract_section(chunk_text)
            chunk_record = {
                "id": f"chunk_{chunk_id:04d}",
                "source_document": doc_path.name,
                "standard_body": body,
                "section": section,
                "text": chunk_text,
                "embedding": None,  # Will be filled below
            }
            all_chunks.append(chunk_record)
            chunk_id += 1

    # Build embeddings
    if use_embeddings and model is not None:
        texts = [c["text"] for c in all_chunks]
        logger.info("Encoding %d chunks with Granite Embedding...", len(texts))
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
        for chunk, emb in zip(all_chunks, embeddings):
            chunk["embedding"] = emb.tolist()
        logger.info("Embeddings complete.")
    else:
        # No embeddings — RAG will fall back to deterministic clause mapping
        logger.warning("No embeddings generated. RAG will use deterministic fallback.")

    return all_chunks


def save_index(chunks: list[dict]) -> None:
    """Save the index to the JSON file."""
    INDEX_FILE.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    logger.info("Saved %d chunks to %s", len(chunks), INDEX_FILE)


def validate_index(chunks: list[dict]) -> None:
    """Validate the built index."""
    if not chunks:
        logger.error("Empty index!")
        return

    bodies = set(c["standard_body"] for c in chunks)
    has_embeddings = sum(1 for c in chunks if c.get("embedding"))

    logger.info("Index validation:")
    logger.info("  Total chunks: %d", len(chunks))
    logger.info("  Standards bodies covered: %s", bodies)
    logger.info("  Chunks with embeddings: %d/%d", has_embeddings, len(chunks))

    # Check all 5 bodies are covered
    required = {"FCC", "IADC", "ISO", "ESA", "COPUOS"}
    missing = required - bodies
    if missing:
        logger.warning("Missing bodies in corpus: %s", missing)
    else:
        logger.info("  All 5 regulatory bodies covered ✓")


if __name__ == "__main__":
    logger.info("Building PHAROS standards embedding index...")

    # Ensure parsed documents exist
    if not PARSED_DIR.exists() or not list(PARSED_DIR.glob("*.md")):
        logger.info("Parsed documents not found. Running parse_standards.py first...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(BACKEND_ROOT / "scripts" / "parse_standards.py")],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            logger.error("parse_standards.py failed: %s", result.stderr)
            sys.exit(1)

    chunks = build_index_with_embeddings()
    validate_index(chunks)
    save_index(chunks)
    print(f"\nIndex built: {len(chunks)} chunks in {INDEX_FILE}")
