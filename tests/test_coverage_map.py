"""Unit and integration tests for Research Coverage Map."""
from fastapi.testclient import TestClient
from src.analysis.coverage_map import ResearchCoverageEngine
from src.api.main import app


def test_coverage_engine_summary():
    engine = ResearchCoverageEngine()
    summary = engine.get_coverage_summary()
    assert summary["total_verified_experiments"] == 200
    assert summary["coverage_completeness_pct"] > 0
    assert "heatmap_grid" in summary
    assert len(summary["heatmap_grid"]) == 20  # 5 O2 bins x 4 Flow bins
    assert "empirical_white_spaces" in summary
    assert len(summary["empirical_white_spaces"]) >= 3


def test_coverage_map_api():
    client = TestClient(app)
    r = client.get("/api/coverage-map")
    assert r.status_code == 200
    data = r.json()
    assert data["total_verified_experiments"] == 200
    assert "material_breakdown" in data
    assert "PMMA" in data["material_breakdown"]
    assert "empirical_white_spaces" in data


def test_coverage_claims_are_dataset_scoped_and_proposals_count_matches():
    engine = ResearchCoverageEngine()
    summary = engine.get_coverage_summary()
    assert summary["scope"] == "current FLARE-X dataset"
    assert "not scientific completeness" in summary["coverage_basis"]
    assert all(c["density"] == "NO_INDEXED_OBSERVATIONS" for c in summary["heatmap_grid"] if c["count"] == 0)
    for proposal in summary["empirical_white_spaces"]:
        assert proposal["status"] == "team_proposal"
        assert proposal["recommended_experiment"].startswith("Team proposal:")
        assert proposal["matching_observations"] == sum(proposal["material_counts"].values())
        assert "current FLARE-X dataset" in proposal["coverage_statement"]

    # An actual indexed match must replace an absence claim, not preserve a canned gap.
    row = engine.df.iloc[0].copy()
    row["material"], row["pressure_kpa"], row["oxygen_pct"], row["flow_cm_s"] = "Nomex", 56.5, 34.0, 20.0
    engine.df = row.to_frame().T
    proposal = engine.get_coverage_summary()["empirical_white_spaces"][0]
    assert proposal["matching_observations"] == 1
    assert proposal["material_counts"]["Nomex"] == 1
    assert proposal["coverage_statement"].startswith("1 matching observations")
