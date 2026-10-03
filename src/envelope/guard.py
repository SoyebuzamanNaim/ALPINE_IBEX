"""Experimental Envelope Guard for FLARE-X.

Enforces strict refusal rules when requested conditions leave published microgravity data.
Calculates domain status: 'in_domain', 'boundary', 'extrapolation', 'unsupported_category'.
Calculates kNN-distance density metrics for sparse-region warnings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.retrieval.nearest import NearestExperimentRetriever

ROOT = Path(__file__).resolve().parents[2]
META_PATH = ROOT / "models" / "model_meta.json"
DATA_PATH = ROOT / "cache" / "experiments.parquet"


class EnvelopeGuard:
    def __init__(self, meta_path: Path = META_PATH, data_path: Path = DATA_PATH):
        if not meta_path.exists():
            raise FileNotFoundError(f"Missing model metadata: {meta_path}")
        self.meta = json.loads(meta_path.read_bytes())
        self.training_range = self.meta["training_range"]
        self.allowed_materials = self.training_range["allowed_materials"]
        self.retriever = NearestExperimentRetriever(data_path)
        self.df = pd.read_parquet(data_path)

    def check(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
    ) -> dict[str, Any]:
        """Check scenario against experimental envelope and return domain status."""
        reasons = []

        # 1. Check material support
        if material not in self.allowed_materials:
            reasons.append({
                "feature": "material",
                "value": material,
                "allowed_values": self.allowed_materials,
                "reason": f"Material '{material}' was not tested in published microgravity datasets."
            })
            nearest = self.retriever.find_nearest(oxygen_pct, pressure_kpa, flow_cm_s, material, k=3)
            return {
                "in_training_range": False,
                "status": "unsupported_category",
                "out_of_range_reasons": reasons,
                "sparse_region_warning": False,
                "warning_message": f"Material '{material}' is not in the published microgravity database.",
                "nearest_experiments": nearest,
                "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
            }

        # 2. Check global min/max bounds
        o2_min = self.training_range["oxygen_pct"]["min"]
        o2_max = self.training_range["oxygen_pct"]["max"]
        if oxygen_pct < o2_min or oxygen_pct > o2_max:
            reasons.append({
                "feature": "oxygen_pct",
                "value": oxygen_pct,
                "train_min": o2_min,
                "train_max": o2_max,
                "reason": f"Oxygen concentration {oxygen_pct}% is outside global training envelope [{o2_min}%, {o2_max}%]."
            })

        p_min = self.training_range["pressure_kpa"]["min"]
        p_max = self.training_range["pressure_kpa"]["max"]
        if pressure_kpa < p_min or pressure_kpa > p_max:
            reasons.append({
                "feature": "pressure_kpa",
                "value": pressure_kpa,
                "train_min": p_min,
                "train_max": p_max,
                "reason": f"Pressure {pressure_kpa} kPa is outside global training envelope [{p_min} kPa, {p_max} kPa]."
            })

        f_min = self.training_range["flow_cm_s"]["min"]
        f_max = self.training_range["flow_cm_s"]["max"]
        if flow_cm_s < f_min or flow_cm_s > f_max:
            reasons.append({
                "feature": "flow_cm_s",
                "value": flow_cm_s,
                "train_min": f_min,
                "train_max": f_max,
                "reason": f"Flow velocity {flow_cm_s} cm/s is outside global training envelope [{f_min} cm/s, {f_max} cm/s]."
            })

        # 3. Check per-material limits
        mat_cfg = self.training_range.get("per_material", {}).get(material)
        if mat_cfg and not reasons:
            m_o2_min = mat_cfg["oxygen_pct"]["min"]
            m_o2_max = mat_cfg["oxygen_pct"]["max"]
            if oxygen_pct < m_o2_min or oxygen_pct > m_o2_max:
                reasons.append({
                    "feature": "oxygen_pct",
                    "value": oxygen_pct,
                    "train_min": m_o2_min,
                    "train_max": m_o2_max,
                    "reason": f"Oxygen concentration {oxygen_pct}% is outside {material} experimental envelope [{m_o2_min}%, {m_o2_max}%]."
                })

            m_p_min = mat_cfg["pressure_kpa"]["min"]
            m_p_max = mat_cfg["pressure_kpa"]["max"]
            if pressure_kpa < m_p_min or pressure_kpa > m_p_max:
                reasons.append({
                    "feature": "pressure_kpa",
                    "value": pressure_kpa,
                    "train_min": m_p_min,
                    "train_max": m_p_max,
                    "reason": f"Pressure {pressure_kpa} kPa is outside {material} experimental envelope [{m_p_min} kPa, {m_p_max} kPa]."
                })

            m_f_min = mat_cfg["flow_cm_s"]["min"]
            m_f_max = mat_cfg["flow_cm_s"]["max"]
            if flow_cm_s < m_f_min or flow_cm_s > m_f_max:
                reasons.append({
                    "feature": "flow_cm_s",
                    "value": flow_cm_s,
                    "train_min": m_f_min,
                    "train_max": m_f_max,
                    "reason": f"Flow velocity {flow_cm_s} cm/s is outside {material} experimental envelope [{m_f_min} cm/s, {m_f_max} cm/s]."
                })

        nearest = self.retriever.find_nearest(oxygen_pct, pressure_kpa, flow_cm_s, material, k=3)

        # If any reason triggered, refuse prediction
        if reasons:
            return {
                "in_training_range": False,
                "status": "extrapolation",
                "out_of_range_reasons": reasons,
                "sparse_region_warning": False,
                "warning_message": "Requested conditions are outside the published experimental envelope. No prediction is made.",
                "nearest_experiments": nearest,
                "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
            }

        # 4. Check boundary proximity (within 5% of range edges or near extinction limit)
        o2_span = o2_max - o2_min
        p_span = p_max - p_min
        f_span = f_max - f_min
        near_edge = (
            abs(oxygen_pct - o2_min) / o2_span <= 0.05 or
            abs(oxygen_pct - o2_max) / o2_span <= 0.05 or
            abs(pressure_kpa - p_min) / p_span <= 0.05 or
            abs(pressure_kpa - p_max) / p_span <= 0.05 or
            abs(flow_cm_s - f_min) / f_span <= 0.05 or
            abs(flow_cm_s - f_max) / f_span <= 0.05 or
            (material == "PMMA" and 16.0 <= oxygen_pct <= 17.5)  # near extinction boundary
        )

        # 5. Density check: kNN average distance to same material
        same_mat_df = self.df[self.df["material"] == material]
        delta_o2 = np.abs(same_mat_df["oxygen_pct"].values - oxygen_pct) / self.retriever.o2_range
        delta_p = np.abs(same_mat_df["pressure_kpa"].values - pressure_kpa) / self.retriever.p_range
        delta_flow = np.abs(same_mat_df["flow_cm_s"].values - flow_cm_s) / self.retriever.flow_range
        knn_dist = np.sort(np.sqrt(delta_o2**2 + delta_p**2 + delta_flow**2))[:3]
        avg_knn_dist = float(np.mean(knn_dist)) if len(knn_dist) > 0 else 1.0

        is_sparse = avg_knn_dist > 0.35
        status = "boundary" if near_edge else "in_domain"

        warning = None
        if is_sparse:
            warning = f"Scenario is in a sparse data region (mean 3-NN distance = {avg_knn_dist:.2f}). Interpret predictions with caution."
        elif status == "boundary":
            warning = "Scenario is near the experimental envelope or flammability regime boundary."

        return {
            "in_training_range": True,
            "status": status,
            "out_of_range_reasons": [],
            "sparse_region_warning": is_sparse,
            "knn_mean_distance": round(avg_knn_dist, 4),
            "warning_message": warning,
            "nearest_experiments": nearest,
            "explanation": None,
        }
