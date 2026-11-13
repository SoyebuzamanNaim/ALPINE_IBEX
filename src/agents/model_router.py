"""Model Router Agent for FLARE-X.

Routes requests to the persisted research classification model,
formats standardized model metadata, and computes class probabilities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.models.baseline import load_trained_model, research_model_readiness

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"


class ModelRouter:
    """Agent that handles model routing, metadata exposure, and probability inference."""

    def __init__(self, model_path: Path = MODEL_PATH, meta_path: Path = META_PATH,
                 data_path: Path = ROOT / "cache" / "experiments.parquet"):
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact missing: {model_path}")
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata missing: {meta_path}")

        self.model_path = model_path
        self.data_path = data_path
        self.model = load_trained_model(model_path, meta_path)
        self.meta = json.loads(meta_path.read_bytes())
        self.classes = list(self.model.classes_)

    def get_model_metadata(self) -> dict[str, Any]:
        """Return standardized model metadata per Section 7 API contract."""
        return {
            "type": self.meta.get("type", "gradient_boosting"),
            "n_train": self.meta.get("n_train"),
            "cv_accuracy": self.meta.get("cv_accuracy"),
            "cv_scheme": self.meta.get(
                "cv_scheme", "LeaveOneGroupOut(group=report_id)"
            ),
            "features": self.meta.get(
                "features", ["oxygen_pct", "pressure_kpa", "flow_cm_s", "material"]
            ),
            **{key: self.meta.get(key) for key in (
                "release_mode", "validation_status", "research_warning", "probability_calibration",
                "majority_baseline_accuracy", "cv_balanced_accuracy", "nested_search",
            )},
        }

    def predict(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
    ) -> dict[str, Any]:
        """Run classification inference and return predicted regime and probabilities."""
        ready, reason = research_model_readiness(self.meta, self.data_path, self.model_path)
        if not ready:
            return {"prediction": None, "probabilities": None, "model": self.get_model_metadata(),
                    "status": "model_unvalidated", "warning_message": reason}
        row = pd.DataFrame([{
            "oxygen_pct": float(oxygen_pct),
            "pressure_kpa": float(pressure_kpa),
            "flow_cm_s": float(flow_cm_s),
            "material": str(material),
        }])

        pred = str(self.model.predict(row)[0])
        raw_probs = self.model.predict_proba(row)[0]
        probabilities = {
            cls: round(float(p), 4) for cls, p in zip(self.classes, raw_probs)
        }

        return {
            "prediction": pred,
            "probabilities": probabilities,
            "model": self.get_model_metadata(),
        }
