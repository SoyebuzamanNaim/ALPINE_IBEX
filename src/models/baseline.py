"""Shared models interface and prediction helper."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"


def load_trained_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model artifact: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def load_model_meta() -> dict[str, Any]:
    if not META_PATH.exists():
        raise FileNotFoundError(f"Missing model metadata: {META_PATH}")
    return json.loads(META_PATH.read_bytes())


class FlameSpreadPredictor:
    def __init__(self):
        self.model = load_trained_model()
        self.meta = load_model_meta()
        self.classes = self.meta["classes"]
        self.training_range = self.meta["training_range"]

    def is_in_range(self, oxygen_pct: float, pressure_kpa: float, flow_cm_s: float, material: str) -> tuple[bool, list[dict[str, Any]]]:
        reasons = []
        # Check material
        allowed_mats = self.training_range["allowed_materials"]
        if material not in allowed_mats:
            reasons.append({
                "feature": "material",
                "value": material,
                "allowed_values": allowed_mats,
                "reason": f"Material '{material}' was not tested in published microgravity datasets."
            })
            return False, reasons

        # Check numeric features
        o2_min = self.training_range["oxygen_pct"]["min"]
        o2_max = self.training_range["oxygen_pct"]["max"]
        if oxygen_pct < o2_min or oxygen_pct > o2_max:
            reasons.append({
                "feature": "oxygen_pct",
                "value": oxygen_pct,
                "train_min": o2_min,
                "train_max": o2_max,
                "reason": f"Oxygen concentration {oxygen_pct}% is outside training envelope [{o2_min}%, {o2_max}%]."
            })

        p_min = self.training_range["pressure_kpa"]["min"]
        p_max = self.training_range["pressure_kpa"]["max"]
        if pressure_kpa < p_min or pressure_kpa > p_max:
            reasons.append({
                "feature": "pressure_kpa",
                "value": pressure_kpa,
                "train_min": p_min,
                "train_max": p_max,
                "reason": f"Pressure {pressure_kpa} kPa is outside training envelope [{p_min} kPa, {p_max} kPa]."
            })

        f_min = self.training_range["flow_cm_s"]["min"]
        f_max = self.training_range["flow_cm_s"]["max"]
        if flow_cm_s < f_min or flow_cm_s > f_max:
            reasons.append({
                "feature": "flow_cm_s",
                "value": flow_cm_s,
                "train_min": f_min,
                "train_max": f_max,
                "reason": f"Flow velocity {flow_cm_s} cm/s is outside training envelope [{f_min} cm/s, {f_max} cm/s]."
            })

        in_range = len(reasons) == 0
        return in_range, reasons

    def predict(self, oxygen_pct: float, pressure_kpa: float, flow_cm_s: float, material: str) -> dict[str, Any]:
        in_range, reasons = self.is_in_range(oxygen_pct, pressure_kpa, flow_cm_s, material)
        if not in_range:
            return {
                "in_training_range": False,
                "out_of_range_reasons": reasons,
                "prediction": None,
                "probabilities": None,
            }

        df_input = pd.DataFrame([{
            "oxygen_pct": oxygen_pct,
            "pressure_kpa": pressure_kpa,
            "flow_cm_s": flow_cm_s,
            "material": material
        }])

        pred_class = self.model.predict(df_input)[0]
        probs = self.model.predict_proba(df_input)[0]
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(self.model.classes_, probs)}

        return {
            "in_training_range": True,
            "out_of_range_reasons": [],
            "prediction": str(pred_class),
            "probabilities": prob_dict,
        }
