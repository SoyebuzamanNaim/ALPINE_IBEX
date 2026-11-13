"""Shared models interface and prediction helper."""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"


def load_trained_model(model_path: Path = MODEL_PATH, meta_path: Path = META_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model artifact: {model_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing model metadata: {meta_path}")
    meta = json.loads(meta_path.read_bytes())
    model_bytes = model_path.read_bytes()
    if hashlib.sha256(model_bytes).hexdigest() != meta.get("model_sha256"):
        raise ValueError(f"Model artifact hash does not match metadata: {model_path}")
    return joblib.load(io.BytesIO(model_bytes))


def load_model_meta() -> dict[str, Any]:
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing model metadata: {META_PATH}")
    return json.loads(META_PATH.read_bytes())


def research_model_readiness(meta: dict[str, Any], data_path: Path = ROOT / "cache" / "experiments.parquet",
                             model_path: Path = MODEL_PATH) -> tuple[bool, str]:
    """Use one integrity and research-release rule for every inference entry point."""
    score, baseline = meta.get("cv_accuracy"), meta.get("majority_baseline_accuracy")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1
           for v in (score, baseline)):
        return False, "Model validation metrics are missing; inference is unavailable."
    if not data_path.exists() or hashlib.sha256(data_path.read_bytes()).hexdigest() != meta.get("dataset_sha256"):
        return False, "Model dataset hash does not match the current experiments table; inference is unavailable."
    if not model_path.exists() or hashlib.sha256(model_path.read_bytes()).hexdigest() != meta.get("model_sha256"):
        return False, "Model artifact hash does not match its metadata; inference is unavailable."
    if score <= baseline:
        return False, (f"Model grouped accuracy ({score:.1%}) does not exceed the majority "
                       f"baseline ({baseline:.1%}); inference is unavailable.")
    return True, "Exploratory research estimates are available; independent external validation is absent."


class FlameSpreadPredictor:
    """Compatibility interface using the same joint-domain and release guards as the API."""

    def __init__(self):
        from src.envelope.guard import EnvelopeGuard

        self.model = load_trained_model()
        self.meta = load_model_meta()
        self.guard = EnvelopeGuard()

    def is_in_range(self, oxygen_pct: float, pressure_kpa: float, flow_cm_s: float, material: str) -> tuple[bool, list[dict[str, Any]]]:
        env = self.guard.check(oxygen_pct, pressure_kpa, flow_cm_s, material)
        return env["in_training_range"] and not env.get("requires_abstention", False), env["out_of_range_reasons"]

    def predict(self, oxygen_pct: float, pressure_kpa: float, flow_cm_s: float, material: str) -> dict[str, Any]:
        env = self.guard.check(oxygen_pct, pressure_kpa, flow_cm_s, material)
        result = {**env, "prediction": None, "probabilities": None}
        if not env["in_training_range"] or env.get("requires_abstention"):
            return result
        ready, reason = research_model_readiness(self.meta)
        if not ready:
            return {**result, "status": "model_unvalidated", "explanation": reason}
        inputs = pd.DataFrame([dict(oxygen_pct=oxygen_pct, pressure_kpa=pressure_kpa, flow_cm_s=flow_cm_s, material=material)])
        return {**result, "prediction": str(self.model.predict(inputs)[0]),
                "probabilities": {str(c): round(float(p), 4) for c, p in zip(self.model.classes_, self.model.predict_proba(inputs)[0])}}
