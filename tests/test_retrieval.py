"""Automated tests and evaluation suite for Evidence Retrieval Engine."""
import pytest
from src.retrieval.nearest import NearestExperimentRetriever
from src.retrieval.corpus_search import ReportCorpusSearcher
from src.retrieval.engine import EvidenceRetrievalEngine


def test_nearest_retrieval_same_material():
    retriever = NearestExperimentRetriever()
    results = retriever.find_nearest(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA", k=3)
    assert len(results) == 3
    # All 3 nearest should be PMMA due to material penalty
    for res in results:
        assert res["material"] == "PMMA"
        assert res["distance"] < 1.0, "Expected close distance for well-sampled region"
        assert "experiment_id" in res
        assert "outcome" in res
        assert "source_url" in res
        assert res["source_url"].startswith("https://ntrs.nasa.gov/citations/")


def test_nearest_retrieval_sorting():
    retriever = NearestExperimentRetriever()
    results = retriever.find_nearest(oxygen_pct=18.0, pressure_kpa=101.3, flow_cm_s=2.0, material="PMMA", k=5)
    distances = [r["distance"] for r in results]
    assert distances == sorted(distances), "Results must be strictly sorted by ascending distance"


def test_similarity_ranking_exposes_score_context_and_limits():
    import math

    retriever = NearestExperimentRetriever()
    results = retriever.find_nearest(21.0, 101.3, 5.0, "Nomex", k=len(retriever.df))
    assert any(r["similarity_ranking"]["material_penalty"] == 10.0 for r in results)
    for record in results:
        ranking = record["similarity_ranking"]
        expected = math.sqrt(sum(d ** 2 for d in ranking["normalized_differences"].values()))
        assert ranking["numeric_distance"] == pytest.approx(expected)
        assert record["distance"] == pytest.approx(expected + ranking["material_penalty"], abs=0.00005)
        row = retriever.df[retriever.df.experiment_id == record["experiment_id"]].iloc[0]
        assert record["sample_geometry"] == row.sample_geometry
        assert record["flow_direction"] == (row.flow_direction if isinstance(row.flow_direction, str) else None)
        assert record["ignition_history"] is None
        summary = record["interpretation"]
        assert summary["method"] == "deterministic_record_template"
        assert "unspecified" in " ".join(summary["conditions_differ"])
        assert "not scientific reliability" in summary["cannot_conclude"]
        assert str(row.outcome) in summary["observed"]


def test_corpus_search_bm25():
    searcher = ReportCorpusSearcher()
    res = searcher.search("PMMA flame spread rods microgravity", top_k=3)
    assert len(res) > 0
    # Should find BASS or BASS-II reports
    rids = [r["report_id"] for r in res]
    assert any(rid in ["20210011385", "20160000593", "20150008961"] for rid in rids)


def test_passage_extraction():
    searcher = ReportCorpusSearcher()
    passage = searcher.extract_supporting_passage("20210011385", ["BASS", "oxygen", "flame"])
    assert len(passage) > 20
    assert "BASS" in passage or "O2" in passage or "oxygen" in passage.lower()


def test_corpus_punctuation_and_decimal_passages(tmp_path):
    import json

    abstract = "PMMA measurements cover 13.6 to 22.2 percent oxygen. Geometry was recorded separately."
    for report_id, title, text in (
        ("1", "PMMA measurements", abstract),
        ("2", "Cotton observations", "A separate cotton experiment was recorded."),
        ("3", "Cellulose observations", "A separate cellulose experiment was recorded."),
    ):
        (tmp_path / f"{report_id}.json").write_text(json.dumps({
            "report_id": report_id, "title": title, "abstract": text, "keywords": [],
        }))
    searcher = ReportCorpusSearcher(tmp_path)
    assert searcher.search("PMMA,")[0]["report_id"] == "1"
    assert searcher.extract_supporting_passage("1", ["PMMA"]) == abstract.split(". Geometry")[0] + "."


def test_evidence_engine_bundle():
    engine = EvidenceRetrievalEngine()
    bundle = engine.retrieve_evidence(oxygen_pct=17.5, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA", k=3)
    assert "scenario" in bundle
    assert "nearest_experiments" in bundle
    assert "cited_reports" in bundle
    assert len(bundle["nearest_experiments"]) == 3
    # Verify every cited report ID exists in the bundle's cited_reports
    for exp in bundle["nearest_experiments"]:
        rid = exp["report_id"]
        assert rid in bundle["cited_reports"]
        assert bundle["cited_reports"][rid]["source_url"] == exp["source_url"]


def test_no_invented_experiment_ids():
    engine = EvidenceRetrievalEngine()
    bundle = engine.retrieve_evidence(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA", k=5)
    for exp in bundle["nearest_experiments"]:
        assert any(exp["experiment_id"].startswith(p) for p in ["BASS", "EXP_", "DF_", "DROP_"])
