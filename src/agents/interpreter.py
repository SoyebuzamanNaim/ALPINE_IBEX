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
        "cotton-fiberglass": "Cotton-Fiberglass",
        "cotton fiberglass": "Cotton-Fiberglass",
        "cellulose": "Cellulose",
        "ashless filter paper": "Cellulose",
        "filter paper": "Cellulose",
        "delrin": "Delrin",
        "polyoxymethylene": "Delrin",
        "pom": "Delrin",
        "nomex": "Nomex",
        "mylar": "Mylar",
        "silicone": "Silicone",
        "ultem": "Ultem",
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

        number = r"(?<![\w.+\-–—])\d+(?:\.\d+)?(?![\w.+\-–—])"

        def malformed_or_range(unit: str) -> bool:
            numeric = r"\d+(?:\.\d+)?"
            bad = rf"(?:[-+−]\s*{numeric}|{numeric}[eE][+-]?\d+|{numeric}\s*(?:-|–|—|to)\s*{numeric})\s*(?:{unit})"
            return re.search(bad, lower) is not None

        def choose_numeric(
            field: str, label: str, values: list[float], missing: str,
            tolerance: float = 1e-6, malformed: bool = False,
        ) -> None:
            if malformed:
                ambiguities.append(f"Malformed or ranged {label} value; provide one non-negative numeric value.")
            elif not values:
                ambiguities.append(missing)
            elif max(values) - min(values) > tolerance:
                ambiguities.append(f"Conflicting {label} values were specified: {', '.join(str(v) for v in values)}.")
            else:
                parsed[field] = values[0]

        # Match longer aliases first so "Cotton-Fiberglass" is one material.
        material_mentions: list[str] = []
        occupied: list[tuple[int, int]] = []
        aliases = {**self.SYNONYMS, "teflon": "Teflon", "kapton": "Kapton"}
        for alias, canonical in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
            for match in re.finditer(rf"(?<!\w){re.escape(alias)}(?!\w)", lower):
                if any(match.start() < end and match.end() > start for start, end in occupied):
                    continue
                occupied.append(match.span())
                material_mentions.append(canonical)
        distinct_materials = sorted(set(material_mentions))
        if len(distinct_materials) > 1:
            ambiguities.append(f"Conflicting material names were specified: {', '.join(distinct_materials)}.")
        elif distinct_materials:
            parsed["material"] = distinct_materials[0]
        else:
            ambiguities.append("Unrecognized or missing solid fuel material.")

        oxygen_explicit: list[float] = []
        oxygen_unlabeled: list[float] = []
        for match in re.finditer(rf"({number})\s*(?:%|pct\b|percent\b)", lower):
            following = lower[match.end():]
            if re.match(r"\s*(?:oxygen|o2)\b", following):
                oxygen_explicit.append(float(match.group(1)))
            elif not re.match(r"\s*(?:relative\s+humidity|humidity|rh)\b", following):
                oxygen_unlabeled.append(float(match.group(1)))
        oxygen_values = oxygen_explicit + oxygen_unlabeled
        if not oxygen_values and "exploration atmosphere" in lower:
            oxygen_values.append(34.0)
        choose_numeric("oxygen_pct", "oxygen", oxygen_values,
                       "Missing oxygen concentration (e.g. '21% O2').",
                       malformed=malformed_or_range(r"%|pct\b|percent\b"))

        pressure_values = [float(match.group(1)) for match in re.finditer(
            rf"({number})\s*(?:kpa|kilopascals?)\b", lower
        )]
        pressure_values.extend(round(float(match.group(1)) * 6.89476, 2) for match in re.finditer(
            rf"({number})\s*psi\b", lower
        ))
        if "sea level" in lower or re.search(r"\b1\s*atm\b", lower):
            pressure_values.append(101.3)
        if "exploration atmosphere" in lower:
            pressure_values.append(56.5)
        choose_numeric("pressure_kpa", "pressure", pressure_values,
                       "Missing pressure specification (e.g. '101.3 kPa' or 'sea level').",
                       tolerance=0.1, malformed=malformed_or_range(r"kpa\b|kilopascals?\b|psi\b"))

        flow_values = [float(match.group(1)) for match in re.finditer(
            rf"({number})\s*(?:cm/s|cm\s*s-1|centimeters?\s*per\s*second)\b", lower
        )]
        if any(term in lower for term in ("quiescent", "zero flow", "stagnant")):
            flow_values.append(0.0)
        choose_numeric("flow_cm_s", "flow", flow_values,
                       "Missing ventilation flow velocity (e.g. '5 cm/s' or 'quiescent').",
                       malformed=malformed_or_range(r"cm/s|cm\s*s-1|centimeters?\s*per\s*second\b"))

        is_valid = len(ambiguities) == 0
        return {
            "parsed_scenario": parsed if is_valid else None,
            "is_valid": is_valid,
            "ambiguities": ambiguities,
            "source_type": "natural_language",
            "raw_text": text,
        }
