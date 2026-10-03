"""Automated tests for Phase 05 Baseline Models."""
from pathlib import Path
import json
import pytest
from src.models.baseline import FlameSpreadPredictor, load_model_meta, load_trained_model

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"
METRICS_PATH = ROOT / "models" / "metrics.json"


def test_model_files_exist():
    assert ARTIFACT_PATH.exists(), "Model artifact must exist"
    assert META_PATH.exists(), "Model metadata must exist"
    assert METRICS_PATH.exists(), "Metrics JSON must exist"


def test_model_meta_schema():
    meta = load_model_meta()
    required_keys = [
        "type", "n_train", "cv_accuracy", "cv_scheme", "features", "classes",
        "trained_at", "dataset_sha256", "training_range", "confusion_matrix"
    ]
    for k in required_keys:
        assert k in meta, f"Missing key in model_meta: {k}"

    assert meta["type"] == "gradient_boosting"
    assert meta["n_train"] >= 100
    assert meta["cv_accuracy"] > meta["majority_baseline_accuracy"], "Model must outperform majority baseline"
    assert "StratifiedGroupKFold" in meta["cv_scheme"], "CV scheme must be grouped"


def test_prediction_in_range():
    predictor = FlameSpreadPredictor()
    res = predictor.predict(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA")
    assert res["in_training_range"] is True
    assert res["out_of_range_reasons"] == []
    assert res["prediction"] in ["no_spread", "marginal_spread", "spread"]
    assert res["probabilities"] is not None
    # Probabilities sum to approximately 1.0
    total_prob = sum(res["probabilities"].values())
    assert pytest.approx(total_prob, rel=1e-2) == 1.0


def test_refusal_when_out_of_range():
    predictor = FlameSpreadPredictor()
    # 55% O2 is above max
    res = predictor.predict(oxygen_pct=55.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA")
    assert res["in_training_range"] is False
    assert res["prediction"] is None
    assert res["probabilities"] is None
    assert len(res["out_of_range_reasons"]) > 0
    assert res["out_of_range_reasons"][0]["feature"] == "oxygen_pct"


def test_refusal_on_unsupported_material():
    predictor = FlameSpreadPredictor()
    res = predictor.predict(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="Titanium")
    assert res["in_training_range"] is False
    assert res["prediction"] is None
    assert any(r["feature"] == "material" for r in res["out_of_range_reasons"])


def test_metrics_comparisons_exist():
    metrics = json.loads(METRICS_PATH.read_bytes())
    models = metrics["models"]
    assert "majority_baseline" in models
    assert "logistic_regression" in models
    assert "random_forest" in models
    assert "gradient_boosting" in models
    # Check that grouped_cv is populated
    assert "accuracy" in models["gradient_boosting"]["grouped_cv"]
    assert "confusion_matrix" in models["gradient_boosting"]["grouped_cv"]
