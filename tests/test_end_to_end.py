"""Phase 12 Full System Integration & End-to-End Test Suite.

Verifies the 6 required flow scenarios from Phase 12:
1. Supported Scenario
2. Boundary Scenario
3. Unsupported Scenario (Extrapolation & Category)
4. Missing Variable / Ambiguity Scenario
5. Sparse Region / Low Evidence Scenario
6. API Failure / Malformed Input Error Handling
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_e2e_1_supported_scenario(client):
    """Case 1: Standard supported scenario (ISS baseline PMMA)."""
    payload = {
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Flow verification: Input -> Model -> Retrieval -> Composer -> Auditor
    assert data["in_training_range"] is True
    assert data["status"] in ["in_domain", "boundary"]
    assert data["prediction"] == "spread"
    assert data["probabilities"]["spread"] > 0.80
    assert data["model"]["n_train"] == 145
    assert len(data["nearest_experiments"]) == 3

    # Grounded citation verification
    first_exp = data["nearest_experiments"][0]
    assert first_exp["report_id"] is not None
    assert "ntrs.nasa.gov" in first_exp["source_url"]
    assert "PMMA" in data["explanation"]


def test_e2e_2_boundary_scenario(client):
    """Case 2: Physical boundary scenario (PMMA near extinction limit)."""
    payload = {
        "oxygen_pct": 16.5,
        "pressure_kpa": 101.3,
        "flow_cm_s": 3.0,
        "material": "PMMA",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["in_training_range"] is True
    assert data["status"] == "boundary"
    assert data["prediction"] in ["marginal_spread", "no_spread"]
    assert data["warning_message"] is not None
    assert "boundary" in data["warning_message"].lower()


def test_e2e_3_unsupported_scenarios(client):
    """Case 3: Unsupported conditions triggering strict refusal."""
    # 3a. Beyond oxygen envelope (48.0% O2)
    res_o2 = client.post("/predict", json={
        "oxygen_pct": 48.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    })
    assert res_o2.status_code == 200
    d_o2 = res_o2.json()
    assert d_o2["in_training_range"] is False
    assert d_o2["prediction"] is None
    assert d_o2["probabilities"] is None
    assert d_o2["status"] == "extrapolation"
    assert any(r["feature"] == "oxygen_pct" for r in d_o2["out_of_range_reasons"])
    assert len(d_o2["nearest_experiments"]) == 3  # Evidence preserved

    # 3b. Unsupported material (Kapton)
    res_mat = client.post("/predict", json={
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "Kapton",
    })
    assert res_mat.status_code == 200
    d_mat = res_mat.json()
    assert d_mat["in_training_range"] is False
    assert d_mat["status"] == "unsupported_category"
    assert any(r["feature"] == "material" for r in d_mat["out_of_range_reasons"])


def test_e2e_4_missing_variable_scenario(client):
    """Case 4: Scenario with missing variables or unresolvable ambiguity."""
    payload = {"query": "Can flames spread on PMMA without air?"}
    res = client.post("/scenario/parse", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["is_valid"] is False
    assert len(data["ambiguities"]) > 0
    # Surfaces missing oxygen and pressure
    assert any("oxygen" in a.lower() for a in data["ambiguities"])
    assert any("pressure" in a.lower() for a in data["ambiguities"])


def test_e2e_5_sparse_region_scenario(client):
    """Case 5: Within bounding box but sparse experimental density."""
    payload = {
        "oxygen_pct": 32.0,
        "pressure_kpa": 60.0,
        "flow_cm_s": 34.0,
        "material": "PMMA",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["in_training_range"] is True
    assert "sparse_region_warning" in data
    assert data["knn_mean_distance"] is not None
    assert isinstance(data["sparse_region_warning"], bool)


def test_e2e_6_api_model_failure_handling(client):
    """Case 6: Malformed payloads, negative bounds, or invalid types fail gracefully."""
    # Negative pressure should fail schema validation with HTTP 422
    res_bad_p = client.post("/predict", json={
        "oxygen_pct": 21.0,
        "pressure_kpa": -50.0,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    })
    assert res_bad_p.status_code == 422

    # String passed to numeric oxygen
    res_bad_type = client.post("/predict", json={
        "oxygen_pct": "not-a-number",
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    })
    assert res_bad_type.status_code == 422

    # Missing mandatory field
    res_missing = client.post("/predict", json={
        "oxygen_pct": 21.0,
    })
    assert res_missing.status_code == 422
