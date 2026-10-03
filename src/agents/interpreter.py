"""Scenario Interpreter Agent for FLARE-X.

Parses natural language or structured requests into the canonical schema.
Exposes ambiguities, converts standard operational synonyms, and validates types.
"""
from __future__ import annotations

import re
from typing import Any


class ScenarioInterpreter:
    """Agent translating natural language queries or raw payloads into canonical flammability input."""

    SYNONYMS = {
        "pmma": "PMMA",
        "plexiglas": "PMMA",
        "acrylic": "PMMA",
        "poly(methyl methacrylate)": "PMMA",
        "cotton": "Cotton",
        "cellulose": "Cellulose",
        "ashless filter paper": "Cellulose",
        "filter paper": "Cellulose",
        "delrin": "Delrin",
        "polyoxymethylene": "Delrin",
        "pom": "Delrin",
        "nomex": "Nomex",
    }

    def __init__(self):
        pass

    def parse(self, input_data: str | dict[str, Any]) -> dict[str, Any]:
        """Parse structured dictionary or natural language string into canonical parameters."""
        if isinstance(input_data, dict):
            return self._parse_dict(input_data)
        elif isinstance(input_data, str):
            return self._parse_text(input_data)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}")

    def _parse_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        ambiguities = []
        parsed = {}

        # 1. Oxygen
        if "oxygen_pct" in payload:
            try:
                parsed["oxygen_pct"] = float(payload["oxygen_pct"])
            except (ValueError, TypeError):
                ambiguities.append("Invalid 'oxygen_pct' value; must be numeric.")
        else:
            ambiguities.append("Missing required parameter: 'oxygen_pct'.")

        # 2. Pressure
        if "pressure_kpa" in payload:
            try:
                parsed["pressure_kpa"] = float(payload["pressure_kpa"])
            except (ValueError, TypeError):
                ambiguities.append("Invalid 'pressure_kpa' value; must be numeric.")
        else:
            ambiguities.append("Missing required parameter: 'pressure_kpa'.")

        # 3. Flow
        if "flow_cm_s" in payload:
            try:
                parsed["flow_cm_s"] = float(payload["flow_cm_s"])
            except (ValueError, TypeError):
                ambiguities.append("Invalid 'flow_cm_s' value; must be numeric.")
        else:
            ambiguities.append("Missing required parameter: 'flow_cm_s'.")

        # 4. Material
        if "material" in payload:
            raw_mat = str(payload["material"]).strip()
            norm_mat = self.SYNONYMS.get(raw_mat.lower(), raw_mat)
            parsed["material"] = norm_mat
        else:
            ambiguities.append("Missing required parameter: 'material'.")

        is_valid = len(ambiguities) == 0
        return {
            "parsed_scenario": parsed if is_valid else None,
            "is_valid": is_valid,
            "ambiguities": ambiguities,
            "source_type": "structured_payload",
        }

    def _parse_text(self, text: str) -> dict[str, Any]:
        ambiguities = []
        parsed: dict[str, Any] = {}
        lower = text.lower()

        # Extract material
        found_mat = None
        for syn, canonical in self.SYNONYMS.items():
            if re.search(rf"\b{re.escape(syn)}\b", lower):
                found_mat = canonical
                break
        if found_mat:
            parsed["material"] = found_mat
        else:
            # Check capitalized tokens
            mat_match = re.search(r"\b(pmma|cotton|cellulose|delrin|nomex|teflon|kapton)\b", lower)
            if mat_match:
                raw = mat_match.group(1)
                parsed["material"] = self.SYNONYMS.get(raw, raw.capitalize())
            else:
                ambiguities.append("Unrecognized or missing solid fuel material.")

        # Extract oxygen
        # e.g., "21% oxygen", "18.5 % o2", "20.9% o2"
        o2_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|pct|percent)\s*(?:oxygen|o2)?", lower)
        if o2_match:
            parsed["oxygen_pct"] = float(o2_match.group(1))
        else:
            ambiguities.append("Missing oxygen concentration (e.g. '21% O2').")

        # Extract pressure
        # e.g., "101.3 kpa", "1 atm", "sea level", "56.5 kpa", "8.2 psi"
        if "sea level" in lower or "1 atm" in lower:
            parsed["pressure_kpa"] = 101.3
        elif "exploration atmosphere" in lower:
            parsed["pressure_kpa"] = 56.5
            if "oxygen_pct" not in parsed:
                parsed["oxygen_pct"] = 34.0
        else:
            p_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kpa|kilopascals?)", lower)
            if p_match:
                parsed["pressure_kpa"] = float(p_match.group(1))
            else:
                psi_match = re.search(r"(\d+(?:\.\d+)?)\s*psi", lower)
                if psi_match:
                    parsed["pressure_kpa"] = round(float(psi_match.group(1)) * 6.89476, 2)
                else:
                    ambiguities.append("Missing pressure specification (e.g. '101.3 kPa' or 'sea level').")

        # Extract flow velocity
        # e.g., "5 cm/s", "quiescent" (0 cm/s), "10.0 cm/s flow"
        if "quiescent" in lower or "zero flow" in lower or "stagnant" in lower:
            parsed["flow_cm_s"] = 0.0
        else:
            f_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm/s|cm\s*s-1|centimeters?\s*per\s*second)", lower)
            if f_match:
                parsed["flow_cm_s"] = float(f_match.group(1))
            else:
                ambiguities.append("Missing ventilation flow velocity (e.g. '5 cm/s' or 'quiescent').")

        is_valid = len(ambiguities) == 0
        return {
            "parsed_scenario": parsed if is_valid else None,
            "is_valid": is_valid,
            "ambiguities": ambiguities,
            "source_type": "natural_language",
            "raw_text": text,
        }
