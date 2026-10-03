"""Evidence Auditor Agent for FLARE-X.

Verifies model outputs, schema conformity, and enforces the strict mathematical
hallucination check required by Challenge Brief Section 8:
- Reject any explanation containing numbers absent from the prediction object.
- Reject any explanation citing report IDs not in nearest_experiments.
"""
from __future__ import annotations

import math
import re
from typing import Any


class EvidenceAuditor:
    """Agent that audits predictions and guards explanation text against ungrounded hallucinations."""

    def __init__(self, numeric_tolerance: float = 0.02):
        self.numeric_tolerance = numeric_tolerance

    def audit_prediction_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Audit the complete prediction payload before presentation."""
        errors = []

        # Check required fields
        for f in ["inputs", "in_training_range", "nearest_experiments"]:
            if f not in payload:
                errors.append(f"Missing mandatory field '{f}' in payload.")

        # Check probability normalization when in domain
        if payload.get("in_training_range") and payload.get("probabilities"):
            probs = payload["probabilities"]
            total = sum(probs.values())
            if not (0.98 <= total <= 1.02):
                errors.append(f"Probabilities do not sum to ~1.0: {total:.4f}")

        # Check nearest experiments
        exps = payload.get("nearest_experiments", [])
        if not isinstance(exps, list) or len(exps) == 0:
            errors.append("Payload lacks nearest historical experiments.")

        return {
            "passed": len(errors) == 0,
            "errors": errors,
        }

    def _extract_allowed_numbers(self, obj: dict[str, Any]) -> list[float]:
        """Collect all authorized numerical quantities from the prediction object."""
        allowed: list[float] = []

        def add_num(val: Any):
            if val is None:
                return
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if not (math.isnan(val) or math.isinf(val)):
                    allowed.append(float(val))
                    # Also allow percentage equivalent if between 0 and 1
                    if 0.0 <= val <= 1.0:
                        allowed.append(float(val * 100))
                    # Also allow decimal equivalent if between 0 and 100
                    if 1.0 < val <= 100.0:
                        allowed.append(float(val / 100))

        # 1. Inputs
        inputs = obj.get("inputs") or {}
        for k in ["oxygen_pct", "pressure_kpa", "flow_cm_s"]:
            add_num(inputs.get(k))

        # 2. Probabilities
        probs = obj.get("probabilities") or {}
        for v in probs.values():
            add_num(v)

        # 3. Model metadata
        model = obj.get("model") or {}
        add_num(model.get("n_train"))
        add_num(model.get("cv_accuracy"))

        # 4. Nearest experiments
        exps = obj.get("nearest_experiments") or []
        for e in exps:
            for k in ["oxygen_pct", "pressure_kpa", "flow_cm_s", "distance", "sample_thickness_mm"]:
                add_num(e.get(k))

        # 5. Allow standard integers 1, 2, 3 (for top-1, top-2, top-3 ranks and 3 nearest)
        allowed.extend([1.0, 2.0, 3.0, float(len(exps))])

        return allowed

    def _number_is_authorized(self, num: float, allowed_numbers: list[float]) -> bool:
        """Check if a candidate number is close to any authorized number."""
        for allowed in allowed_numbers:
            if abs(num - allowed) <= max(self.numeric_tolerance, abs(allowed) * 0.01):
                return True
        return False

    def audit_explanation(
        self,
        explanation_text: str,
        prediction_obj: dict[str, Any],
    ) -> dict[str, Any]:
        """Strict numerical and citation audit of the generated explanation.

        Rejects text if any number or report ID was not present in the prediction object.
        """
        if not explanation_text:
            return {"is_valid": True, "hallucinated_numbers": [], "invalid_citations": []}

        allowed_numbers = self._extract_allowed_numbers(prediction_obj)

        # Authorized report IDs
        allowed_report_ids = set()
        for e in prediction_obj.get("nearest_experiments", []):
            if "report_id" in e and e["report_id"]:
                allowed_report_ids.add(str(e["report_id"]))
            if "experiment_id" in e and e["experiment_id"]:
                allowed_report_ids.add(str(e["experiment_id"]))

        # Extract all numbers from text (avoid matching dates like 2026 or report ID substrings if part of report_id)
        # First, mask out allowed report IDs in text so their numeric parts aren't extracted as standalone numbers
        sanitized_text = explanation_text
        for rid in allowed_report_ids:
            sanitized_text = sanitized_text.replace(rid, " [REPORT_ID] ")

        # Match numbers: e.g. 18.5, -4.2, 21%, 101.3
        raw_tokens = re.findall(r"(?<![A-Za-z0-9_-])-?\d+(?:\.\d+)?%?", sanitized_text)

        hallucinated_numbers = []
        for tok in raw_tokens:
            is_pct = tok.endswith("%")
            val_str = tok.rstrip("%")
            try:
                val = float(val_str)
                # If followed by %, value in text is val %
                if not self._number_is_authorized(val, allowed_numbers):
                    hallucinated_numbers.append(tok)
            except ValueError:
                continue

        # Extract citations (pattern for NASA/TM, NTRS, or report IDs)
        citation_matches = re.findall(
            r"\b(?:NASA/(?:TM|CR|TP)[-\s]\d{4}[-\s]\d+|NTRS\s+\d+|EXP_[A-Z0-9_]+)\b",
            explanation_text,
            flags=re.IGNORECASE,
        )
        invalid_citations = []
        for cite in citation_matches:
            # Check if this cite matches any allowed report ID
            normalized_cite = cite.strip().replace(" ", "-")
            matched = any(
                normalized_cite.lower() in allowed_id.replace(" ", "-").lower() or
                allowed_id.replace(" ", "-").lower() in normalized_cite.lower()
                for allowed_id in allowed_report_ids
            )
            if not matched:
                invalid_citations.append(cite)

        is_valid = (len(hallucinated_numbers) == 0) and (len(invalid_citations) == 0)

        return {
            "is_valid": is_valid,
            "hallucinated_numbers": list(set(hallucinated_numbers)),
            "invalid_citations": list(set(invalid_citations)),
            "reasons": (
                f"Hallucinated numbers: {hallucinated_numbers}; "
                f"Unauthorized citations: {invalid_citations}"
                if not is_valid else "Explanation strictly grounded in prediction object."
            ),
        }
