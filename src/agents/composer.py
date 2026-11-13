"""Explanation Composer Agent for FLARE-X.

Uses deterministic templates to describe model outputs and indexed observations.
The auditor checks numbers and citation identifiers, not scientific entailment.
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
        prediction = prediction_obj.get("prediction")
        probs = prediction_obj.get("probabilities") or {}
        probability = probs.get(prediction)
        estimate = (
            f"Exploratory model estimate: {prediction} for {inputs.get('material')} at "
            f"{inputs.get('oxygen_pct')}% oxygen, {inputs.get('pressure_kpa')} kPa and "
            f"{inputs.get('flow_cm_s')} cm/s. "
            if prediction else "No model estimate is available. "
        )
        if probability is not None:
            estimate += f"Estimated class probability: {probability * 100:.1f}%; not validated across reports. "

        exps = prediction_obj.get("nearest_experiments") or []
        citations = "; ".join(
            f"{e.get('report_id') or e.get('experiment_id')} (observed: {e.get('outcome')})"
            for e in exps[:2] if (e.get("report_id") or e.get("experiment_id")) and e.get("outcome")
        )
        selected = exps[0].get("interpretation", {}) if exps else {}
        observed = selected.get("observed") or citations or "No indexed observation is available."
        differences = " ".join(selected.get("conditions_differ", [])) or (
            "Geometry, flow direction and ignition history are not specified in the query; agreement is unknown."
        )
        limits = selected.get("cannot_conclude") or (
            "Similarity does not measure scientific reliability or establish the requested outcome or safety."
        )
        return (
            f"{estimate}What was observed: {observed} "
            f"Which conditions differ: {differences} "
            f"What cannot be concluded: {limits} "
            f"Source records: {citations or 'none'}. Summary method: deterministic template."
        )

    def compose(
        self,
        prediction_obj: dict[str, Any],
        candidate_text: str | None = None,
    ) -> dict[str, Any]:
        """Check numbers/citations; this is not a semantic claim checker or an LLM call."""
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
            # Numeric/citation agreement cannot validate a candidate's scientific claims.
            det_text = self.compose_deterministic(prediction_obj)
            return {
                "explanation": det_text,
                "audited": True,
                "source": "deterministic_candidate_not_enabled" if audit_res["is_valid"] else "deterministic_fallback_audit_failed",
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
