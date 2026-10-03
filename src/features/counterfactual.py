"""Counterfactual Engine for FLARE-X.

Enables interactive parameter perturbation, multi-step parameter sweeps,
regime boundary detection, and safety margin estimation with strict envelope checking.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.envelope.guard import EnvelopeGuard
from src.retrieval.nearest import NearestExperimentRetriever

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"
DATA_PATH = ROOT / "cache" / "experiments.parquet"


class CounterfactualEngine:
    """Engine for exploring what-if scenarios and parameter sweeps across flammability regimes."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        meta_path: Path = META_PATH,
        data_path: Path = DATA_PATH,
    ):
        if not model_path.exists():
            raise FileNotFoundError(f"Model file missing: {model_path}")
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file missing: {meta_path}")

        self.model = joblib.load(model_path)
        self.meta = json.loads(meta_path.read_bytes())
        self.guard = EnvelopeGuard(meta_path=meta_path, data_path=data_path)
        self.retriever = NearestExperimentRetriever(data_path=data_path)
        self.df = pd.read_parquet(data_path)
        self.classes = list(self.model.classes_)

    def evaluate_scenario(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
    ) -> dict[str, Any]:
        """Evaluate a single operational scenario through the envelope guard and predictive model."""
        env = self.guard.check(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
        )

        inputs = {
            "oxygen_pct": float(oxygen_pct),
            "pressure_kpa": float(pressure_kpa),
            "flow_cm_s": float(flow_cm_s),
            "material": str(material),
        }

        if not env["in_training_range"]:
            return {
                "inputs": inputs,
                "in_training_range": False,
                "status": env["status"],
                "out_of_range_reasons": env["out_of_range_reasons"],
                "prediction": None,
                "probabilities": None,
                "confidence": None,
                "nearest_experiments": env["nearest_experiments"],
                "sparse_region_warning": False,
                "warning_message": env["warning_message"],
                "explanation": env["explanation"],
            }

        # Model inference
        row = pd.DataFrame([inputs])
        pred = str(self.model.predict(row)[0])
        prob_array = self.model.predict_proba(row)[0]
        probabilities = {cls: round(float(p), 4) for cls, p in zip(self.classes, prob_array)}
        confidence = probabilities[pred]

        return {
            "inputs": inputs,
            "in_training_range": True,
            "status": env["status"],
            "out_of_range_reasons": [],
            "prediction": pred,
            "probabilities": probabilities,
            "confidence": confidence,
            "nearest_experiments": env["nearest_experiments"],
            "sparse_region_warning": env.get("sparse_region_warning", False),
            "knn_mean_distance": env.get("knn_mean_distance"),
            "warning_message": env.get("warning_message"),
            "explanation": None,
        }

    def compute_perturbation(
        self,
        baseline: dict[str, Any],
        changes: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute delta between a baseline scenario and a modified counterfactual scenario."""
        cf_inputs = dict(baseline)
        cf_inputs.update(changes)

        base_res = self.evaluate_scenario(
            oxygen_pct=baseline["oxygen_pct"],
            pressure_kpa=baseline["pressure_kpa"],
            flow_cm_s=baseline["flow_cm_s"],
            material=baseline["material"],
        )

        cf_res = self.evaluate_scenario(
            oxygen_pct=cf_inputs["oxygen_pct"],
            pressure_kpa=cf_inputs["pressure_kpa"],
            flow_cm_s=cf_inputs["flow_cm_s"],
            material=cf_inputs["material"],
        )

        # Calculate variable deltas
        changed_vars = {}
        for k, new_v in changes.items():
            old_v = baseline.get(k)
            delta = None
            if isinstance(old_v, (int, float)) and isinstance(new_v, (int, float)):
                delta = round(new_v - old_v, 4)
            changed_vars[k] = {
                "baseline": old_v,
                "counterfactual": new_v,
                "delta": delta,
            }

        # Prediction delta
        base_pred = base_res["prediction"]
        cf_pred = cf_res["prediction"]
        pred_changed = base_pred != cf_pred

        # Probability deltas
        prob_deltas = {}
        if base_res["probabilities"] and cf_res["probabilities"]:
            for cls in self.classes:
                prob_deltas[cls] = round(
                    cf_res["probabilities"][cls] - base_res["probabilities"][cls], 4
                )

        # Evidence delta
        base_exp_ids = [e["experiment_id"] for e in base_res.get("nearest_experiments", [])]
        cf_exp_ids = [e["experiment_id"] for e in cf_res.get("nearest_experiments", [])]
        shared_ids = list(set(base_exp_ids).intersection(cf_exp_ids))
        added_ids = [eid for eid in cf_exp_ids if eid not in base_exp_ids]
        removed_ids = [eid for eid in base_exp_ids if eid not in cf_exp_ids]

        return {
            "baseline": base_res,
            "counterfactual": cf_res,
            "changed_variables": changed_vars,
            "prediction_delta": {
                "changed": pred_changed,
                "from_regime": base_pred,
                "to_regime": cf_pred,
            },
            "probability_deltas": prob_deltas,
            "evidence_delta": {
                "shared_experiment_ids": shared_ids,
                "added_experiment_ids": added_ids,
                "removed_experiment_ids": removed_ids,
            },
            "scientific_disclaimer": (
                "Counterfactual predictions reflect empirical gradient-boosted patterns "
                "from published NASA microgravity experiments. They do not constitute formal "
                "causal proof and must be validated against physical Navier-Stokes/combustion models."
            ),
        }

    def run_sweep(
        self,
        baseline: dict[str, Any],
        param: str,
        start: float,
        end: float,
        steps: int = 25,
    ) -> dict[str, Any]:
        """Run a 1D parameter sweep to map regime boundaries and find transition thresholds."""
        if steps < 2:
            raise ValueError("Sweep requires at least 2 steps.")
        if param not in ["oxygen_pct", "pressure_kpa", "flow_cm_s"]:
            raise ValueError(f"Continuous sweep parameter '{param}' not supported.")

        values = np.linspace(start, end, steps)
        points = []
        transitions = []
        prev_pt = None

        for val in values:
            scenario = dict(baseline)
            scenario[param] = round(float(val), 3)
            res = self.evaluate_scenario(
                oxygen_pct=scenario["oxygen_pct"],
                pressure_kpa=scenario["pressure_kpa"],
                flow_cm_s=scenario["flow_cm_s"],
                material=scenario["material"],
            )

            pt = {
                param: round(float(val), 3),
                "in_training_range": res["in_training_range"],
                "status": res["status"],
                "prediction": res["prediction"],
                "probabilities": res["probabilities"],
                "nearest_experiments": res["nearest_experiments"],
                "warning_message": res.get("warning_message"),
            }
            points.append(pt)

            # Detect regime boundary transition between consecutive valid points
            if prev_pt is not None:
                p_prev = prev_pt["prediction"]
                p_curr = pt["prediction"]
                if p_prev is not None and p_curr is not None and p_prev != p_curr:
                    transitions.append({
                        "param": param,
                        "from_regime": p_prev,
                        "to_regime": p_curr,
                        "transition_interval": [prev_pt[param], pt[param]],
                        "midpoint": round((prev_pt[param] + pt[param]) / 2, 3),
                        "evidence_before": prev_pt["nearest_experiments"][:2],
                        "evidence_after": pt["nearest_experiments"][:2],
                    })

            prev_pt = pt

        # Safety margin to extinction / no_spread
        base_val = float(baseline[param])
        safety_margin = None
        for t in transitions:
            if "no_spread" in (t["from_regime"], t["to_regime"]):
                boundary_mid = t["midpoint"]
                safety_margin = {
                    "boundary_midpoint": boundary_mid,
                    "baseline_value": base_val,
                    "delta_to_boundary": round(base_val - boundary_mid, 3),
                    "is_safe_side": base_val < boundary_mid if start < end else base_val > boundary_mid,
                }
                break

        return {
            "parameter": param,
            "range": [float(start), float(end)],
            "steps": steps,
            "baseline": baseline,
            "points": points,
            "transitions": transitions,
            "safety_margin": safety_margin,
            "total_transitions": len(transitions),
        }
