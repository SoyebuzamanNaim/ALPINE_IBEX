"""Unified Evidence Retrieval Engine for FLARE-X."""
from __future__ import annotations

from typing import Any
from src.retrieval.nearest import NearestExperimentRetriever
from src.retrieval.corpus_search import ReportCorpusSearcher


class EvidenceRetrievalEngine:
    def __init__(self):
        self.nearest_retriever = NearestExperimentRetriever()
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
        if any(exp["distance"] > 0.5 for exp in nearest):
            caveats.append("Nearest experimental points are relatively sparse in this region of the operational envelope.")
        if flow_cm_s < 1.0:
            caveats.append("Low flow velocities (<1 cm/s) in microgravity approach the quiescent extinction limit where radiative loss dominates.")

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
        }
