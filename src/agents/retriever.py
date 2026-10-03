"""Evidence Retriever Agent for FLARE-X.

Wraps NearestExperimentRetriever and BM25 ReportCorpusSearch.
Strict invariant: cannot invent evidence or modify experimental numbers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.retrieval.corpus_search import ReportCorpusSearcher
from src.retrieval.nearest import NearestExperimentRetriever

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
CORPUS_DIR = ROOT / "cache" / "report_corpus"


class EvidenceRetrieverAgent:
    """Agent responsible for retrieving empirical experiment rows and report context passages."""

    def __init__(
        self,
        data_path: Path = DATA_PATH,
        corpus_dir: Path = CORPUS_DIR,
    ):
        self.retriever = NearestExperimentRetriever(data_path=data_path)
        self.corpus_search = ReportCorpusSearcher(corpus_dir=corpus_dir)
        self.df = self.retriever.df

    def retrieve(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
        k: int = 3,
    ) -> dict[str, Any]:
        """Retrieve top k nearest empirical experiments and relevant report passages."""
        # 1. Structured table retrieval
        nearest_exps = self.retriever.find_nearest(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
            k=k,
        )

        # 2. Text corpus retrieval
        query = f"{material} flame spread microgravity {oxygen_pct}% oxygen {pressure_kpa} kPa {flow_cm_s} cm/s"
        passages = self.corpus_search.search(query, top_k=2)

        return {
            "query": {
                "oxygen_pct": oxygen_pct,
                "pressure_kpa": pressure_kpa,
                "flow_cm_s": flow_cm_s,
                "material": material,
            },
            "nearest_experiments": nearest_exps,
            "supporting_passages": passages,
            "experiment_count": len(nearest_exps),
        }
