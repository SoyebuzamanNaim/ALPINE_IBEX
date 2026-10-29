"""Unit and integration tests for Conflict Explorer."""
import pytest
from fastapi.testclient import TestClient
from src.analysis.conflict_explorer import ConflictExplorerEngine
from src.api.main import app


def test_conflict_explorer_canonical_cases():
    engine = ConflictExplorerEngine()
    cases = engine.list_canonical_cases()
    assert len(cases) >= 4
    case_ids = [c["case_id"] for c in cases]
    assert "bass2_vs_saffire" in case_ids
    assert "drop_tower_vs_bass2" in case_ids


def test_conflict_explorer_study_comparison():
    engine = ConflictExplorerEngine()
    res = engine.compare_canonical_studies("BASS-II", "Saffire")
    assert res["verdict"] == "COMPLEMENTARY_DIFFERENT_REGIMES"
    assert 0.0 <= res["comparability_score"] <= 1.0
    assert len(res["dimensions"]) >= 4
    assert "scientific_reconciliation" in res
    assert "citations" in res


def test_conflict_explorer_experiment_comparison():
    engine = ConflictExplorerEngine()
    res = engine.compare_experiments("BASS2_B1_5", "BASS2_B6_5")
    assert "comparability_score" in res
    assert res["verdict"] in ["HIGHLY_COMPARABLE", "COMPLEMENTARY_DIFFERENT_REGIMES", "STRUCTURAL_MISMATCH_NON_COMPARABLE"]
    assert "citations" in res


def test_conflict_explorer_api_endpoints():
    client = TestClient(app)
    
    # 1. Cases
    r = client.get("/api/conflict/cases")
    assert r.status_code == 200
    assert "cases" in r.json()

    # 2. Profiles
    r = client.get("/api/conflict/profiles")
    assert r.status_code == 200
    assert "profiles" in r.json()

    # 3. Compare studies
    r = client.post("/api/conflict/compare-studies", json={"study_a": "BASS-II", "study_b": "Drop_Tower_Olson"})
    assert r.status_code == 200
    data = r.json()
    assert data["study_a_id"] == "BASS-II"
    assert "Transient" in data["scientific_reconciliation"] or "drop" in data["scientific_reconciliation"].lower()

    # 4. Error on unknown study
    r = client.post("/api/conflict/compare-studies", json={"study_a": "UNKNOWN_STUDY", "study_b": "BASS-II"})
    assert r.status_code == 400
