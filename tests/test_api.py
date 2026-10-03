"""Automated test suite for FLARE-X FastAPI Backend (Phase 10)."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["dataset_rows"] == 145
    assert data["model_type"] == "gradient_boosting"
    assert "PMMA" in data["allowed_materials"]


def test_post_predict_in_domain(client):
    payload = {
        "oxygen_pct": 21.0,
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
    assert data["prediction"] in ["spread", "marginal_spread", "no_spread"]
    assert set(data["probabilities"].keys()) == {"no_spread", "marginal_spread", "spread"}
    assert data["model"]["type"] == "gradient_boosting"
    assert data["model"]["n_train"] == 145
    assert data["model"]["cv_accuracy"] > 0.70
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


def test_get_experiments(client):
    res = client.get("/experiments?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 145
    assert len(data["experiments"]) == 10

    # Filter by material
    mat_res = client.get("/experiments?material=PMMA&limit=150")
    assert mat_res.status_code == 200
    mat_data = mat_res.json()
    assert mat_data["total"] == 92
    assert all(r["material"] == "PMMA" for r in mat_data["experiments"])


def test_get_model(client):
    res = client.get("/model")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "gradient_boosting"
    assert data["n_train"] == 145
    assert "confusion_matrix" in data
    assert "training_range" in data


def test_get_boundary(client):
    res = client.get("/boundary?material=PMMA&pressure_kpa=101.3&o2_steps=12&flow_steps=12")
    assert res.status_code == 200
    data = res.json()
    assert data["material"] == "PMMA"
    assert len(data["oxygen_grid"]) == 12
    assert len(data["flow_grid"]) == 12
    assert len(data["grid_predictions"]) == 12
    assert len(data["real_experiments"]) > 0


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
    assert res.status_code == 200
    data = res.json()
    assert data["prediction_delta"]["changed"] is True
    assert "probability_deltas" in data
    assert "scientific_disclaimer" in data


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
    assert res.status_code == 200
    data = res.json()
    assert data["parameter"] == "oxygen_pct"
    assert len(data["points"]) == 11
    assert data["total_transitions"] >= 1
    assert data["safety_margin"] is not None


def test_post_scenario_parse(client):
    payload = {"query": "Evaluate 18.5% O2 at sea level with 10 cm/s flow for PMMA"}
    res = client.post("/scenario/parse", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["parsed_scenario"]["material"] == "PMMA"
    assert data["parsed_scenario"]["oxygen_pct"] == 18.5


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
