"""Compare recorded conditions without inferring reliability or physical causes."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"

# These identifiers group indexed rows; they are not complete study specifications.
STUDY_PROFILES = {
    "BASS-II": {"title": "BASS-II", "prefix": "BASS-II", "report_id": "20210011385"},
    "Saffire": {"title": "Saffire I–VI", "prefix": "Saffire-", "report_id": "20170008805"},
    "Drop_Tower_Olson": {"title": "GRC drop-tower extinction (Ferkul)", "prefix": "GRC Zero Gravity", "report_id": "19890014267"},
    "Exploration_Atmospheres": {"title": "Exploration atmospheres", "prefix": "Exploration Atmospheres", "report_id": "20080034883"},
    "SoFIE_MIST": {"title": "SoFIE-MIST", "prefix": "SoFIE", "report_id": "20200000361"},
}

COMPARISON_CASES = [
    {"case_id": "bass2_vs_saffire", "name": "BASS-II and Saffire: compare recorded conditions", "study_a": "BASS-II", "study_b": "Saffire"},
    {"case_id": "drop_tower_vs_bass2", "name": "Drop tower and BASS-II: compare recorded context", "study_a": "Drop_Tower_Olson", "study_b": "BASS-II"},
    {"case_id": "normobaric_vs_exploration", "name": "BASS-II and exploration-atmosphere observations", "study_a": "BASS-II", "study_b": "Exploration_Atmospheres"},
    {"case_id": "sofie_vs_drop_tower", "name": "SoFIE-MIST and drop tower: inspect missing indexed context", "study_a": "SoFIE_MIST", "study_b": "Drop_Tower_Olson"},
]

DIMENSIONS = [
    ("material", "Material", ""),
    ("sample_geometry", "Sample geometry", ""),
    ("sample_thickness_mm", "Sample thickness", " mm"),
    ("flow_direction", "Flow direction", ""),
    ("oxygen_pct", "Initial oxygen", "%"),
    ("pressure_kpa", "Pressure", " kPa"),
    ("flow_cm_s", "Airflow", " cm/s"),
    ("burn_duration_s", "Burn duration", " s"),
    ("ignition_history", "Ignition history", ""),
]


class ConflictExplorerEngine:
    """Describe differences in the current indexed table, leaving unknowns unknown."""

    def __init__(self, data_path: Path = DATA_PATH):
        self.df = pd.read_parquet(data_path)

    def list_canonical_cases(self) -> list[dict[str, Any]]:
        return COMPARISON_CASES

    def _study_rows(self, key: str) -> pd.DataFrame:
        if key not in STUDY_PROFILES:
            raise ValueError(f"Unknown study profile '{key}'.")
        return self.df[self.df["investigation"].str.startswith(STUDY_PROFILES[key]["prefix"])]

    @staticmethod
    def _values(rows: pd.DataFrame, field: str, unit: str) -> tuple[str, bool]:
        if field not in rows or rows.empty:
            return "Not recorded in the indexed dataset", False
        values = rows[field].dropna()
        if values.empty:
            return "Not recorded in the indexed dataset", False
        if pd.api.types.is_numeric_dtype(values):
            lo, hi = float(values.min()), float(values.max())
            text = f"{lo}{unit}" if lo == hi else f"{lo}–{hi}{unit}"
        else:
            text = ", ".join(sorted(str(value) for value in values.unique()))
        complete = len(values) == len(rows)
        return text + (" (some rows missing)" if not complete else ""), complete

    def list_study_profiles(self) -> dict[str, Any]:
        profiles = {}
        for key, profile in STUDY_PROFILES.items():
            rows = self._study_rows(key)
            profiles[key] = {
                "key": key, "title": profile["title"], "report_id": profile["report_id"],
                "citation": f"NTRS {profile['report_id']}", "indexed_observations": len(rows),
                "scale": self._values(rows, "sample_geometry", "")[0],
                "flow_type": self._values(rows, "flow_direction", "")[0],
                "atmosphere": self._values(rows, "pressure_kpa", " kPa")[0],
                "materials": sorted(rows["material"].dropna().unique().tolist()),
                "scope": "current FLARE-X dataset; not a complete study specification",
            }
        return profiles

    @staticmethod
    def _citation(rows: pd.DataFrame, title: str, report_id: str) -> dict[str, Any]:
        reports = [
            {"report_id": str(rid), "url": str(group.iloc[0]["source_url"])}
            for rid, group in rows.groupby("report_id", observed=True, sort=True)
        ]
        if not reports:
            reports = [{"report_id": report_id, "url": f"https://ntrs.nasa.gov/citations/{report_id}"}]
        primary = reports[0]
        return {"name": title, **primary, "citation": f"NTRS {primary['report_id']}", "reports": reports}

    def _compare(self, rows_a: pd.DataFrame, rows_b: pd.DataFrame, id_a: str, id_b: str,
                 title_a: str, title_b: str, report_a: str, report_b: str) -> dict[str, Any]:
        dimensions, differences = [], []
        for field, label, unit in DIMENSIONS:
            a, complete_a = self._values(rows_a, field, unit)
            b, complete_b = self._values(rows_b, field, unit)
            status = "UNKNOWN" if not complete_a or not complete_b else "MATCH" if a == b else "DIFFERENT"
            if status == "DIFFERENT":
                differences.append(label)
            dimensions.append({
                "dimension": label, "study_a": a, "study_b": b, "status": status,
                "physical_impact": "Agreement cannot be assessed from the indexed records." if status == "UNKNOWN" else
                    "Recorded values differ; their effect is not inferred." if status == "DIFFERENT" else
                    "Recorded values match; this does not establish equivalent test protocols.",
            })
        unknown = sum(d["status"] == "UNKNOWN" for d in dimensions)
        matched = sum(d["status"] == "MATCH" for d in dimensions)
        outcome_a = sorted(rows_a["outcome"].unique().tolist())
        outcome_b = sorted(rows_b["outcome"].unique().tolist())
        return {
            "study_a_id": id_a, "study_b_id": id_b, "study_a_title": title_a, "study_b_title": title_b,
            "comparability_score": None,
            "comparison_method": "deterministic_recorded_conditions",
            "verdict": "CONTEXT_DIFFERS" if differences else "INCOMPLETE_CONTEXT" if unknown else "RECORDED_VALUES_MATCH",
            "verdict_summary": f"{len(differences)} recorded dimensions differ; {unknown} cannot be assessed. No scientific comparability score is assigned.",
            "matching_dimensions": matched, "unknown_dimensions": unknown,
            "dimensions": dimensions, "key_physical_differences": differences,
            "scientific_reconciliation": (
                f"Indexed labels: {title_a}: {', '.join(outcome_a) or 'no indexed observations'}; "
                f"{title_b}: {', '.join(outcome_b) or 'no indexed observations'}. "
                "This comparison describes recorded conditions. It does not explain why outcomes differ. "
                "Study ranges aggregate different tests; overlapping ranges do not demonstrate matched experiments. "
                "Review original observations, geometry, flow direction and ignition protocol before interpretation."
            ),
            "cautionary_guidance": "Missing context remains unknown. Matching recorded values do not justify numerical pooling, causal claims or safety clearance.",
            "scope": "current FLARE-X dataset",
            "citations": {"study_a": self._citation(rows_a, title_a, report_a),
                          "study_b": self._citation(rows_b, title_b, report_b)},
        }

    def compare_canonical_studies(self, key_a: str, key_b: str) -> dict[str, Any]:
        rows_a, rows_b = self._study_rows(key_a), self._study_rows(key_b)
        a, b = STUDY_PROFILES[key_a], STUDY_PROFILES[key_b]
        return self._compare(rows_a, rows_b, key_a, key_b, a["title"], b["title"], a["report_id"], b["report_id"])

    def compare_experiments(self, exp_id_a: str, exp_id_b: str) -> dict[str, Any]:
        a = self.df[self.df["experiment_id"] == exp_id_a]
        b = self.df[self.df["experiment_id"] == exp_id_b]
        if a.empty or b.empty:
            raise ValueError("One or both experiment IDs are absent from the current FLARE-X dataset.")
        return self._compare(a, b, exp_id_a, exp_id_b, exp_id_a, exp_id_b,
                             str(a.iloc[0]["report_id"]), str(b.iloc[0]["report_id"]))
