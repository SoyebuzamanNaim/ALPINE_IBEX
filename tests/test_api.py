"""Automated test suite for FLARE-X FastAPI Backend (Phase 10)."""
import pytest
import numpy as np
from fastapi.testclient import TestClient
from src.api.main import app, _mask_conflicting_grid_points, _mask_joint_domain_grid_points
from src.api.schemas import CounterfactualRequest


@pytest.fixture
def client():
    return TestClient(app)


def test_get_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "degraded"
    assert data["model_ready"] is False
    assert data["dataset_rows"] == 200
    assert data["model_type"] == "gradient_boosting"
    assert "PMMA" in data["allowed_materials"]


def test_api_rejects_oversized_bodies_and_long_free_text(client):
    oversized = b'{"query":"' + (b"x" * 66_000) + b'"}'
    too_large = client.post("/scenario/parse", content=oversized, headers={"content-type": "application/json"})
    assert too_large.status_code == 413

    too_long_query = client.post("/scenario/parse", json={"query": "x" * 2001})
    assert too_long_query.status_code == 422

    too_long_material = client.post("/predict", json={
        "oxygen_pct": 19.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0,
        "material": "x" * 65,
    })
    assert too_long_material.status_code == 422


def test_post_predict_in_domain(client):
    payload = {
        "oxygen_pct": 19.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Verify Section 7 contract shape
    assert data["inputs"] == payload
    assert data["in_training_range"] is True
    assert data["out_of_range_reasons"] == []
    assert data["status"] == "model_unvalidated"
    assert data["prediction"] is None
    assert data["probabilities"] is None
    assert data["model"]["type"] == "gradient_boosting"
    assert data["model"]["n_train"] == 200
    # Records what the honest data gives, and is not a target. Removing the 49
    # unsupported rows left four report groups, so report-grouped CV trains on 21
    # rows whenever BASS-II is the held-out fold. The requirement this used to
    # stand for lives in test_models.py::test_model_beats_majority_baseline, which
    # is a strict xfail because the model does not currently meet it. See reports/REBUILT_MODEL_EVALUATION.md Addendum 7.
    assert data["model"]["cv_accuracy"] > 0.50
    assert len(data["nearest_experiments"]) == 3
    first_exp = data["nearest_experiments"][0]
    assert "report_id" in first_exp
    assert "source_url" in first_exp
    assert "outcome" in first_exp
    assert "explanation" in data
    assert len(data["explanation"]) > 20


def test_post_predict_out_of_range_refusal(client):
    # 45.0% O2 is out of range
    payload = {
        "oxygen_pct": 45.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Strict Section 7 Refusal Shape
    assert data["in_training_range"] is False
    assert data["prediction"] is None
    assert data["probabilities"] is None
    assert len(data["out_of_range_reasons"]) > 0
    assert data["out_of_range_reasons"][0]["feature"] == "oxygen_pct"
    assert "train_min" in data["out_of_range_reasons"][0]
    assert "train_max" in data["out_of_range_reasons"][0]
    # Nearest experiments MUST still be returned
    assert len(data["nearest_experiments"]) == 3
    assert "Requested conditions are outside" in data["explanation"]


def test_predict_abstains_when_identical_inputs_have_conflicting_outcomes(client):
    response = client.post("/predict", json={
        "oxygen_pct": 18.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 3.0,
        "material": "PMMA",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["in_training_range"] is True
    assert result["status"] == "conflicting_evidence"
    assert result["prediction"] is None
    assert result["probabilities"] is None
    assert {"BASS2_O3a_3", "BASS2_O3b_3"} <= {
        item["experiment_id"] for item in result["nearest_experiments"]
    }


def test_predict_abstains_for_single_condition_material(client):
    response = client.post("/predict", json={
        "oxygen_pct": 26.2,
        "pressure_kpa": 70.7,
        "flow_cm_s": 20.0,
        "material": "Cotton",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["in_training_range"] is True
    assert result["status"] == "insufficient_material_evidence"
    assert result["prediction"] is None
    assert result["probabilities"] is None
    assert result["sparse_region_warning"] is True


def test_predict_withholds_result_if_final_audit_fails(client, monkeypatch):
    import src.api.main as api_main

    monkeypatch.setattr(api_main, "_model_readiness", lambda: (True, "Test-ready model"))
    monkeypatch.setattr(api_main.orchestrator.auditor, "audit_prediction_payload", lambda payload: {
        "passed": False, "errors": ["Injected audit failure"]
    })
    response = client.post("/predict", json={
        "oxygen_pct": 19.0, "pressure_kpa": 101.3,
        "flow_cm_s": 5.0, "material": "PMMA",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "audit_failed"
    assert result["prediction"] is None
    assert result["probabilities"] is None


def test_boundary_mask_excludes_conflicting_grid_cells():
    mask = _mask_conflicting_grid_points(
        np.array([18.0, 19.0]), np.array([3.0, 3.0]),
        material="PMMA", pressure_kpa=101.3,
        valid_mask=np.array([True, True]),
    )
    assert mask.tolist() == [False, True]


def test_boundary_mask_excludes_jointly_unsupported_cells():
    mask = _mask_joint_domain_grid_points(
        np.array([22.0]), np.array([20.0]),
        material="Cellulose", pressure_kpa=70.0,
        valid_mask=np.array([True]),
    )
    assert mask.tolist() == [False]


def test_boundary_mask_excludes_single_condition_material():
    mask = _mask_joint_domain_grid_points(
        np.array([26.2]), np.array([20.0]),
        material="Cotton", pressure_kpa=70.7,
        valid_mask=np.array([True]),
    )
    assert mask.tolist() == [False]


def test_get_experiments(client):
    res = client.get("/experiments?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 200
    assert len(data["experiments"]) == 10

    # Filter by material
    mat_res = client.get("/experiments?material=PMMA&limit=150")
    assert mat_res.status_code == 200
    mat_data = mat_res.json()
    assert mat_data["total"] == 151
    assert all(r["material"] == "PMMA" for r in mat_data["experiments"])


def test_get_model(client):
    res = client.get("/model")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "gradient_boosting"
    assert data["n_train"] == 200
    assert "confusion_matrix" in data
    assert "training_range" in data


def test_get_boundary(client):
    res = client.get("/boundary?material=PMMA&pressure_kpa=101.3&o2_steps=12&flow_steps=12")
    assert res.status_code == 503
    assert "majority baseline" in res.json()["detail"]


def test_post_counterfactual(client):
    payload = {
        "baseline": {
            "oxygen_pct": 21.0,
            "pressure_kpa": 101.3,
            "flow_cm_s": 5.0,
            "material": "PMMA",
        },
        "changes": {"oxygen_pct": 16.5},
    }
    res = client.post("/counterfactual", json=payload)
    assert res.status_code == 503
    assert "majority baseline" in res.json()["detail"]


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"unknown": 17.0},
        {"oxygen_pct": -1.0},
        {"pressure_kpa": "not a number"},
        {"flow_cm_s": None},
        {"material": None},
        {"oxygen_pct": True},
        {"oxygen_pct": "1e309"},
    ],
)
def test_counterfactual_rejects_invalid_changes_before_model_gate(client, changes):
    response = client.post("/counterfactual", json={
        "baseline": {
            "oxygen_pct": 21.0, "pressure_kpa": 101.3,
            "flow_cm_s": 5.0, "material": "PMMA",
        },
        "changes": changes,
    })
    assert response.status_code == 422


def test_counterfactual_normalizes_valid_numeric_changes():
    request = CounterfactualRequest.model_validate({
        "baseline": {
            "oxygen_pct": 21.0, "pressure_kpa": 101.3,
            "flow_cm_s": 5.0, "material": "PMMA",
        },
        "changes": {"oxygen_pct": "19.5"},
    })
    assert request.changes == {"oxygen_pct": 19.5}


def test_post_sweep(client):
    payload = {
        "baseline": {
            "oxygen_pct": 21.0,
            "pressure_kpa": 101.3,
            "flow_cm_s": 5.0,
            "material": "PMMA",
        },
        "param": "oxygen_pct",
        "start": 21.0,
        "end": 16.0,
        "steps": 11,
    }
    res = client.post("/sweep", json=payload)
    assert res.status_code == 503
    assert "majority baseline" in res.json()["detail"]


def test_post_scenario_parse(client):
    payload = {"query": "Evaluate 18.5% O2 at sea level with 10 cm/s flow for PMMA"}
    res = client.post("/scenario/parse", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["parsed_scenario"]["material"] == "PMMA"
    assert data["parsed_scenario"]["oxygen_pct"] == 18.5


def test_scenario_parse_reports_conflicting_values(client):
    response = client.post("/scenario/parse", json={
        "query": "PMMA at 21% O2 or 34% O2, 101.3 kPa, 5 cm/s",
    })
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] is False
    assert result["parsed_scenario"] is None
    assert any("oxygen" in item.lower() for item in result["ambiguities"])


def test_get_datasets(client):
    res = client.get("/datasets")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 20
    assert len(data["investigations"]) >= 20


def test_get_source_document(client):
    # Fetch known report from corpus
    res = client.get("/sources/20140011099")
    assert res.status_code == 200
    doc = res.json()
    assert doc["report_id"] == "20140011099"
    assert "BASS" in doc["title"]


def test_get_root_serves_frontend(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "FLARE-X" in res.text
    assert "flammability-boundary-canvas" in res.text
