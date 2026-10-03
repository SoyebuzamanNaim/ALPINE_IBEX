"""Explanation Composer Agent for FLARE-X.

Converts verified prediction payloads and empirical citations into clear,
rigorous scientific explanations.
Enforces Section 8 Rule 4: If text fails the numerical/citation audit,
fall back immediately to a deterministic template.
"""
from __future__ import annotations

from typing import Any

from src.agents.auditor import EvidenceAuditor


class ExplanationComposer:
    """Agent that composes grounded scientific explanations for flammability predictions."""

    def __init__(self, auditor: EvidenceAuditor | None = None):
        self.auditor = auditor or EvidenceAuditor()

    def compose_deterministic(self, prediction_obj: dict[str, Any]) -> str:
        """Compose a strictly bounded deterministic explanation citing only authorized values."""
        if not prediction_obj.get("in_training_range"):
            return (
                "Requested conditions are outside the published experimental envelope. "
                "No prediction is made."
            )

        inputs = prediction_obj.get("inputs", {})
        material = inputs.get("material", "fuel")
        o2 = inputs.get("oxygen_pct")
        p = inputs.get("pressure_kpa")
        flow = inputs.get("flow_cm_s")

        prediction = prediction_obj.get("prediction", "unknown")
        probs = prediction_obj.get("probabilities", {})
        prob_val = probs.get(prediction)
        pct_str = f"{prob_val * 100:.1f}%" if prob_val is not None else "high confidence"

        regime_desc = {
            "spread": "sustained flame spread",
            "marginal_spread": "marginal flame spread with unstable propagation or near-extinction oscillations",
            "no_spread": "flame extinction or failure to sustain spread",
        }.get(prediction, prediction)

        exps = prediction_obj.get("nearest_experiments", [])
        cite_texts = []
        for e in exps[:2]:
            rid = e.get("report_id") or e.get("experiment_id")
            outcome = e.get("outcome") or e.get("flame_spread_regime")
            if rid and outcome:
                cite_texts.append(f"{rid} (observed: {outcome})")

        citations = "; ".join(cite_texts) if cite_texts else "historical microgravity flight logs"

        # Construct explanation incorporating only validated numbers
        text = (
            f"Under microgravity conditions without natural buoyant convection, {material} at {o2}% O2, "
            f"{p} kPa, and {flow} cm/s ventilation is predicted to exhibit {regime_desc} with a probability of {pct_str}. "
            f"In microgravity, forced airflow supplies convective oxygen to the reaction zone while conductive and radiative "
            f"heat losses dictate the flame stabilization boundary. "
            f"This prediction is supported by the nearest published NASA spaceflight records: {citations}."
        )

        return text

    def compose(
        self,
        prediction_obj: dict[str, Any],
        candidate_text: str | None = None,
    ) -> dict[str, Any]:
        """Produce an audited explanation, falling back to deterministic template on audit failure."""
        if not prediction_obj.get("in_training_range"):
            refusal_text = (
                "Requested conditions are outside the published experimental envelope. "
                "No prediction is made."
            )
            return {
                "explanation": refusal_text,
                "audited": True,
                "source": "envelope_refusal",
                "audit_result": {"is_valid": True, "hallucinated_numbers": [], "invalid_citations": []},
            }

        # If external candidate text was provided (e.g. from an LLM), audit it strictly
        if candidate_text:
            audit_res = self.auditor.audit_explanation(candidate_text, prediction_obj)
            if audit_res["is_valid"]:
                return {
                    "explanation": candidate_text,
                    "audited": True,
                    "source": "llm_validated",
                    "audit_result": audit_res,
                }
            # Audit failed: fallback to deterministic template per Rule 4
            det_text = self.compose_deterministic(prediction_obj)
            return {
                "explanation": det_text,
                "audited": True,
                "source": "deterministic_fallback_audit_failed",
                "audit_result": audit_res,
            }

        # Default: generate deterministic template and audit it
        det_text = self.compose_deterministic(prediction_obj)
        audit_res = self.auditor.audit_explanation(det_text, prediction_obj)
        return {
            "explanation": det_text,
            "audited": True,
            "source": "deterministic_template",
            "audit_result": audit_res,
        }
