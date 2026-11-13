"""Provenance & Claim-Level Citation Service for FLARE-X Evidence Atlas.

Provides fine-grained source traceability for every NASA microgravity combustion observation.
Allows researchers and judges to trace any AI claim or empirical data point back to its
recorded NASA report reference and available source-location fields.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
REPORT_CORPUS_DIR = ROOT / "cache" / "report_corpus"


class ProvenanceService:
    """Service providing granular claim-level citation tracing."""

    def __init__(
        self,
        data_path: Path = DATA_PATH,
        corpus_dir: Path = REPORT_CORPUS_DIR,
    ):
        self.data_path = data_path
        self.corpus_dir = corpus_dir
        self._registry: dict[str, dict[str, Any]] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        # Canonical rows are authoritative; an older registry must not override conditions.
        df = pd.read_parquet(self.data_path)
        self._registry = {
            str(row["experiment_id"]): {
                key: None if pd.isna(value) else value
                for key, value in row.items()
            }
            for row in df.to_dict(orient="records")
        }

    def get_provenance(self, experiment_id: str) -> Optional[dict[str, Any]]:
        """Retrieve complete provenance and citation card for an experiment ID."""
        record = self._registry.get(experiment_id)
        if not record:
            return None

        # Enrich with report corpus metadata if available
        report_id = record.get("report_id")
        corpus_meta = self._get_report_corpus_info(report_id)

        return {
            **record,
            "report_title": corpus_meta.get("title", f"NTRS record {report_id}"),
            "authors": corpus_meta.get("authors", []),
            "publication_year": corpus_meta.get("year"),
            "doi": corpus_meta.get("doi"),
            "document_type": corpus_meta.get("document_type"),
            "summary_method": "source_record_lookup",
        }

    def query_provenance(
        self,
        material: Optional[str] = None,
        verification_tier: Optional[str] = None,
        investigation: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Filter provenance records by material, tier, investigation, or keyword."""
        items = list(self._registry.values())

        if material:
            items = [i for i in items if i.get("material", "").lower() == material.lower()]

        if verification_tier:
            items = [i for i in items if i.get("verification_tier", "") == verification_tier]

        if investigation:
            items = [i for i in items if investigation.lower() in i.get("investigation", "").lower()]

        if search_query:
            q = search_query.lower()
            items = [
                i
                for i in items
                if q in i.get("experiment_id", "").lower()
                or q in i.get("exact_source_citation", "").lower()
                or q in i.get("extraction_notes", "").lower()
                or q in i.get("report_id", "").lower()
            ]

        total = len(items)
        paginated = items[offset : offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "records": paginated,
        }

    def _get_report_corpus_info(self, report_id: str) -> dict[str, Any]:
        """Fetch corpus doc info for a given report ID."""
        if not report_id or not self.corpus_dir.exists():
            return {}
        p = self.corpus_dir / f"{report_id}.json"
        if p.exists():
            try:
                return json.loads(p.read_bytes())
            except (OSError, ValueError):
                return {}
        return {}
