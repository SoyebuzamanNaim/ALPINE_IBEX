"""Check that checked-in model artifacts match the canonical dataset and metrics."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"
METRICS_PATH = ROOT / "models" / "metrics.json"


def fail(message: str) -> None:
    raise SystemExit(f"Artifact check failed: {message}")


def main() -> None:
    for path in (DATA_PATH, MODEL_PATH, META_PATH, METRICS_PATH):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    dataset_hash = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    if meta.get("dataset_sha256") != dataset_hash:
        fail("model metadata dataset SHA-256 does not match cache/experiments.parquet")
    if metrics.get("dataset_sha256") != dataset_hash:
        fail("metrics dataset SHA-256 does not match cache/experiments.parquet")

    row_count = len(pd.read_parquet(DATA_PATH))
    if meta.get("n_train") != row_count or metrics.get("n_train") != row_count:
        fail(f"dataset has {row_count} rows but model metadata/metrics disagree")

    model_results = metrics.get("models", {})
    gb_report = model_results.get("gradient_boosting", {}).get("report_grouped_cv", {})
    baseline_report = model_results.get("majority_baseline", {}).get("report_grouped_cv", {})
    for key, report in (("cv_accuracy", gb_report), ("majority_baseline_accuracy", baseline_report)):
        expected = report.get("accuracy")
        actual = meta.get(key)
        if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
            fail(f"missing {key} in metadata or report-grouped metrics")
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
            fail(f"model metadata {key}={actual} does not match metrics.json value {expected}")

    model = joblib.load(MODEL_PATH)
    if not callable(getattr(model, "predict", None)) or not callable(getattr(model, "predict_proba", None)):
        fail("serialized model does not expose predict and predict_proba")
    print(f"Artifacts verified: {row_count} rows, SHA-256 {dataset_hash}")


if __name__ == "__main__":
    main()
