"""Unified Evidence Retrieval Engine for FLARE-X."""
from __future__ import annotations

from typing import Any
import hashlib
from src.retrieval.nearest import NearestExperimentRetriever
from src.retrieval.corpus_search import ReportCorpusSearcher


class EvidenceRetrievalEngine:
    def __init__(self):
        self.nearest_retriever = NearestExperimentRetriever()
        self.dataset_sha256 = hashlib.sha256(self.nearest_retriever.data_path.read_bytes()).hexdigest()
        self.corpus_searcher = ReportCorpusSearcher()

    def retrieve_evidence(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
        k: int = 3,
    ) -> dict[str, Any]:
        """Generate a complete EvidenceBundle for a given fire scenario."""
        # 1. Retrieve nearest experiments
        nearest = self.nearest_retriever.find_nearest(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
            k=k,
        )

        # 2. Extract cited reports and supporting passages
        unique_report_ids = sorted(list({exp["report_id"] for exp in nearest}))
        cited_reports = {}
        for rid in unique_report_ids:
            doc = self.corpus_searcher.get_report(rid)
            if doc:
                keywords = [material, "oxygen", "flame", "extinction", "flow"]
                passage = self.corpus_searcher.extract_supporting_passage(rid, keywords)
                cited_reports[rid] = {
                    "report_id": rid,
                    "title": doc.get("title"),
                    "abstract": doc.get("abstract"),
                    "source_url": doc.get("source_url"),
                    "supporting_passage": passage,
                }

        # 3. Formulate scientific caveats
        caveats = []
        caveats.append("Similarity ranking measures numerical proximity, not scientific reliability or coverage of the requested scenario.")
        caveats.append("Geometry, flow direction and ignition protocol are not represented in this four-input query. Review the original source context.")

        return {
            "scenario": {
                "oxygen_pct": oxygen_pct,
                "pressure_kpa": pressure_kpa,
                "flow_cm_s": flow_cm_s,
                "material": material,
            },
            "nearest_experiments": nearest,
            "cited_reports": cited_reports,
            "scientific_caveats": caveats,
            "scope": "current FLARE-X dataset",
            "dataset_sha256": self.dataset_sha256,
            "material_counts": {str(material): int(count) for material, count in self.nearest_retriever.df["material"].value_counts().items()},
            "summary_method": "deterministic_record_template",
            "prediction": None,
            "selected_result": nearest[0]["interpretation"] if nearest else None,
        }
