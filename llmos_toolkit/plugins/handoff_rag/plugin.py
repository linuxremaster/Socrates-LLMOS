# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Handoff RAG plugin — local retrieval over the project's own markdown
files, plus structured handoff-document generation. No network, no API
key, no ML framework. Same architectural philosophy as the RAGdb paper
(SQLite storage + pure-NumPy statistical vectorization instead of a
deep-learning embedding model) — built directly rather than depending on
an unreviewed third-party package.

What this is NOT: semantic (meaning-based) search. TF-IDF + cosine
similarity is a statistical keyword-overlap method — it finds chunks
that share vocabulary with the query, not chunks that mean the same
thing using different words. That's a real capability gap versus a
transformer-embedding-based RAG system. Stated plainly because
overclaiming "semantic search" here would be the same failure mode
`claim_flag` exists to catch elsewhere in this toolkit.

Storage: a single SQLite file (default handoff_rag.db). Two tables:
  documents(path, sha256, last_modified)
  chunks(doc_id, chunk_index, heading, content)
TF-IDF vectors are computed fresh at query time from stored raw chunk
text, not persisted — simplest-correct choice for a corpus this size
(tens to low hundreds of files); avoids stale-vector bugs entirely.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from llmos_toolkit.core.paths import get_rag_path

DB_FILE = get_rag_path("handoff_rag.db")

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-z0-9]+")


def _connect(db_path: Path = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE NOT NULL,
            sha256 TEXT NOT NULL,
            last_indexed TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            heading TEXT,
            content TEXT NOT NULL
        )
    """)
    return conn


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunk_markdown(text: str) -> list[tuple[str, str]]:
    """Split into (heading, body) pairs at markdown headers of any level.
    Content before the first heading gets heading '(preamble)'."""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("(whole file)", text.strip())] if text.strip() else []

    chunks = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.append(("(preamble)", preamble))

    for i, m in enumerate(matches):
        heading = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        chunks.append((heading, body))
    return chunks


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def cmd_index(args: argparse.Namespace) -> int:
    conn = _connect(Path(args.db))
    roots = [Path(p) for p in args.dirs]
    indexed, skipped, removed = 0, 0, 0

    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix in (".md", ".txt"):
            files.append(root)
        elif root.is_dir():
            files.extend(p for p in root.rglob("*") if p.suffix in (".md", ".txt"))

    seen_paths = set()
    for f in sorted(files):
        path_str = str(f)
        seen_paths.add(path_str)
        digest = _sha256(f)

        row = conn.execute("SELECT id, sha256 FROM documents WHERE path = ?", (path_str,)).fetchone()
        if row and row[1] == digest:
            skipped += 1
            continue

        text = f.read_text(encoding="utf-8", errors="replace")
        chunk_pairs = _chunk_markdown(text)

        if row:
            doc_id = row[0]
            conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            conn.execute(
                "UPDATE documents SET sha256 = ?, last_indexed = ? WHERE id = ?",
                (digest, datetime.now(timezone.utc).isoformat(), doc_id),
            )
        else:
            cur = conn.execute(
                "INSERT INTO documents (path, sha256, last_indexed) VALUES (?, ?, ?)",
                (path_str, digest, datetime.now(timezone.utc).isoformat()),
            )
            doc_id = cur.lastrowid

        for idx, (heading, body) in enumerate(chunk_pairs):
            if body:
                conn.execute(
                    "INSERT INTO chunks (doc_id, chunk_index, heading, content) VALUES (?, ?, ?, ?)",
                    (doc_id, idx, heading, body),
                )
        indexed += 1

    # Remove documents that no longer exist on disk
    existing_paths = {r[0] for r in conn.execute("SELECT path FROM documents")}
    for stale_path in existing_paths - seen_paths:
        conn.execute("DELETE FROM documents WHERE path = ?", (stale_path,))
        removed += 1

    conn.commit()
    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    conn.close()

    print(f"Indexed: {indexed} file(s) changed/new, {skipped} unchanged, {removed} removed from index.")
    print(f"Total chunks in index: {total_chunks}")
    return 0


def _configure_index(p: argparse.ArgumentParser) -> None:
    p.add_argument("dirs", nargs="+", help="Files or directories to index (.md/.txt)")
    p.add_argument("--db", default=str(DB_FILE))


def _build_tfidf(chunk_texts: list[str]) -> tuple[np.ndarray, list[str]]:
    """Pure-NumPy TF-IDF. Returns (L2-normalized doc-term matrix, vocabulary)."""
    tokenized = [_tokenize(t) for t in chunk_texts]
    vocab: dict[str, int] = {}
    for tokens in tokenized:
        for tok in tokens:
            if tok not in vocab:
                vocab[tok] = len(vocab)

    n_docs, n_terms = len(chunk_texts), len(vocab)
    tf = np.zeros((n_docs, n_terms), dtype=np.float64)
    for i, tokens in enumerate(tokenized):
        for tok in tokens:
            tf[i, vocab[tok]] += 1

    df = np.count_nonzero(tf, axis=0)
    idf = np.log((n_docs + 1) / (df + 1)) + 1.0  # smoothed, sklearn-style

    tfidf = tf * idf
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    tfidf_normalized = tfidf / norms
    return tfidf_normalized, list(vocab.keys())


def _query_vector(query: str, vocab: list[str]) -> np.ndarray:
    vocab_index = {t: i for i, t in enumerate(vocab)}
    tokens = _tokenize(query)
    vec = np.zeros(len(vocab), dtype=np.float64)
    for tok in tokens:
        if tok in vocab_index:
            vec[vocab_index[tok]] += 1
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def cmd_query(args: argparse.Namespace) -> int:
    conn = _connect(Path(args.db))
    rows = conn.execute(
        "SELECT chunks.id, documents.path, chunks.heading, chunks.content "
        "FROM chunks JOIN documents ON chunks.doc_id = documents.id"
    ).fetchall()
    conn.close()

    if not rows:
        print("Index is empty. Run rag-index first.")
        return 1

    ids, paths, headings, contents = zip(*rows)
    tfidf_matrix, vocab = _build_tfidf(list(contents))
    q_vec = _query_vector(args.query, vocab)

    cosine_scores = tfidf_matrix @ q_vec  # both L2-normalized -> dot product = cosine similarity

    query_lower = args.query.lower()
    substring_boost = np.array(
        [0.15 if query_lower in c.lower() else 0.0 for c in contents]
    )
    final_scores = cosine_scores + substring_boost

    top_k = min(args.k, len(final_scores))
    top_indices = np.argsort(final_scores)[::-1][:top_k]

    if final_scores[top_indices[0]] == 0:
        print("No matches — query shares no vocabulary with the indexed content.")
        print("Reminder: this is keyword/TF-IDF overlap, not semantic search.")
        return 0

    for rank, i in enumerate(top_indices, 1):
        if final_scores[i] <= 0:
            break
        print(f"[{rank}] score={final_scores[i]:.3f}  {paths[i]}  §{headings[i]}")
        snippet = contents[i][:200].replace("\n", " ")
        print(f"    {snippet}{'...' if len(contents[i]) > 200 else ''}")
    return 0


def _configure_query(p: argparse.ArgumentParser) -> None:
    p.add_argument("query")
    p.add_argument("-k", type=int, default=5, help="Number of results (default 5)")
    p.add_argument("--db", default=str(DB_FILE))


def cmd_handoff(args: argparse.Namespace) -> int:
    """Generate a structured handoff doc — pointers to what changed and
    what's open, not pasted content. Matches the LLMOS_Session_Handoff_
    Memory.md pattern already used successfully in this project."""
    conn = _connect(Path(args.db))
    docs = conn.execute("SELECT path, last_indexed FROM documents ORDER BY last_indexed DESC").fetchall()
    conn.close()

    lines = [
        f"# Handoff — generated {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Indexed documents (most recently indexed first)",
    ]
    for path, last_indexed in docs[:15]:
        lines.append(f"- `{path}` (indexed {last_indexed})")
    if len(docs) > 15:
        lines.append(f"- ...and {len(docs) - 15} more. Query the index rather than reading this list further.")

    lines += [
        "",
        "## How to catch up",
        "1. Run `rag-query \"<topic>\"` against this index for anything specific.",
        "2. This handoff doc is a pointer set, not a summary — it does not",
        "   substitute for reading the actual kernel/state files it points to.",
        "",
        "## Not automated here",
        "- Open items / TODO state: read the project's own TODO tracking directly.",
        "- Anything requiring an API call: out of scope for this local-only tool.",
    ]

    output = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output)
    return 0


def _configure_handoff(p: argparse.ArgumentParser) -> None:
    p.add_argument("--db", default=str(DB_FILE))
    p.add_argument("--output", help="Write to this file instead of stdout")


def register(registry) -> None:
    registry.register("rag-index", cmd_index,
                       help="Index markdown/text files into the local retrieval database",
                       configure_parser=_configure_index, source="handoff_rag")
    registry.register("rag-query", cmd_query,
                       help="TF-IDF + substring-boost search over the indexed content (keyword search, not semantic)",
                       configure_parser=_configure_query, source="handoff_rag")
    registry.register("rag-handoff", cmd_handoff,
                       help="Generate a pointer-based handoff document from the index",
                       configure_parser=_configure_handoff, source="handoff_rag")
