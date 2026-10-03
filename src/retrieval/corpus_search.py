"""Corpus search and passage retrieval over NASA Technical Reports."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT / "cache" / "report_corpus"


class ReportCorpusSearcher:
    def __init__(self, corpus_dir: Path = CORPUS_DIR):
        if not corpus_dir.exists():
            raise FileNotFoundError(f"Missing report corpus directory: {corpus_dir}")
        self.corpus_dir = corpus_dir
        self.documents: list[dict[str, Any]] = []
        self.doc_tokens: list[list[str]] = []
        self.doc_by_id: dict[str, dict[str, Any]] = {}

        for p in sorted(corpus_dir.glob("*.json")):
            doc = json.loads(p.read_bytes())
            self.documents.append(doc)
            self.doc_by_id[str(doc["report_id"])] = doc
            
            # Combine text for indexing
            text = f"{doc.get('title', '')} {doc.get('abstract', '')} {' '.join(doc.get('keywords', []))}".lower()
            tokens = text.split()
            self.doc_tokens.append(tokens)

        if self.doc_tokens:
            self.bm25 = BM25Okapi(self.doc_tokens)
        else:
            self.bm25 = None

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        """Fetch report metadata and abstract by report_id."""
        return self.doc_by_id.get(str(report_id))

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """BM25 search over report corpus."""
        if not self.bm25 or not self.documents:
            return []

        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = dict(self.documents[idx])
                doc["score"] = round(float(scores[idx]), 4)
                results.append(doc)
        return results

    def extract_supporting_passage(self, report_id: str, keywords: list[str]) -> str:
        """Extract the most relevant sentences from the report abstract."""
        doc = self.get_report(report_id)
        if not doc or not doc.get("abstract"):
            return "Abstract unavailable."

        abstract = doc["abstract"]
        sentences = [s.strip() for s in abstract.split(".") if len(s.strip()) > 20]
        scored = []
        for s in sentences:
            score = sum(1 for kw in keywords if kw.lower() in s.lower())
            scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s for sc, s in scored[:2] if sc > 0]
        if top_sentences:
            return ". ".join(top_sentences) + "."
        return sentences[0] + "." if sentences else abstract[:200] + "..."
