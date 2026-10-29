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
