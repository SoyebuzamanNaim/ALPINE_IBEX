"""End-to-End Test Suite for FLARE-X Evidence Atlas Workflow.

Validates the full NASA Space Apps 2026 winning demonstration storyline:
1. Grounded Evidence Retrieval & Claim-level Provenance
2. Multi-study Comparability & Conflict Explorer
3. Research Coverage Map & Empirical White Spaces
4. 4-Tier Scientific State Protocol Enforcement
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_full_evidence_atlas_workflow():
    # 1. System Health & Governance
    health = client.get("/health").json()
    assert health["status"] == "healthy"
    assert health["dataset_rows"] == 145

    # 2. Evidence Retrieval with Claim-Level Citations
    pred_res = client.post("/predict", json={
        "material": "PMMA",
        "oxygen_pct": 20.6,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
    }).json()

    assert pred_res["in_training_range"] is True
    assert pred_res["prediction"] == "spread"
    assert len(pred_res["nearest_experiments"]) >= 3

    # Check that nearest experiment has verified citation
    nearest = pred_res["nearest_experiments"][0]
    exp_id = nearest["experiment_id"]
    prov_res = client.get(f"/api/provenance/{exp_id}").json()
    assert prov_res["experiment_id"] == exp_id
    assert "NASA" in prov_res["exact_source_citation"]
    assert prov_res["verification_tier"] in ["VERIFIED_FLIGHT_TABLE", "VERIFIED_DROP_TOWER_TABLE"]

    # 3. Scientific Evidence Conflict Explorer: Microscale BASS-II vs Large-Scale Saffire
    conflict_res = client.post("/api/conflict/compare-studies", json={
        "study_a": "BASS-II",
        "study_b": "Saffire",
    }).json()

    assert conflict_res["verdict"] == "COMPLEMENTARY_DIFFERENT_REGIMES"
    assert 0.40 <= conflict_res["comparability_score"] <= 0.60
    assert any("Scale" in d["dimension"] for d in conflict_res["dimensions"])
    assert "radiative" in conflict_res["scientific_reconciliation"].lower()

    # 4. Research Coverage Map & Empirical White Spaces
    coverage_res = client.get("/api/coverage-map").json()
    assert coverage_res["total_verified_experiments"] == 145
    assert coverage_res["coverage_completeness_pct"] > 0
    assert len(coverage_res["empirical_white_spaces"]) >= 3

    # Check for Artemis ECLSS knowledge gap
    gap_ids = [g["gap_id"] for g in coverage_res["empirical_white_spaces"]]
    assert "GAP_HYPOBARIC_HIGH_O2_HIGH_FLOW" in gap_ids

    # 5. Out-of-Domain Abstention (Tier 3)
    refusal_res = client.post("/predict", json={
        "material": "PMMA",
        "oxygen_pct": 45.0,  # Exceeds NASA flight domain
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
    }).json()

    assert refusal_res["in_training_range"] is False
    assert refusal_res["prediction"] is None
    assert refusal_res["probabilities"] is None
    assert len(refusal_res["out_of_range_reasons"]) > 0
