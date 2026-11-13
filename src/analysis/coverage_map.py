"""Count observations in the current FLARE-X dataset and label team proposals.

Dataset absence is not evidence of a gap in the wider literature or of safety.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"


O2_BINS = [
    {"id": "o2_hypoxic", "label": "< 18% O2 (Hypoxic/Quench)", "min": 0.0, "max": 18.0},
    {"id": "o2_low_norm", "label": "18 - 20.9% O2 (Sub-normoxic)", "min": 18.0, "max": 20.9},
    {"id": "o2_normoxic", "label": "20.9 - 25% O2 (Normoxic/Air)", "min": 20.9, "max": 25.0},
    {"id": "o2_exploration", "label": "25 - 32% O2 (Exploration Atm.)", "min": 25.0, "max": 32.0},
    {"id": "o2_enriched", "label": "> 32% O2 (High Enrichment)", "min": 32.0, "max": 100.0},
]

FLOW_BINS = [
    {"id": "flow_quench", "label": "0 - 1 cm/s (Quiescent/Quench)", "min": 0.0, "max": 1.0},
    {"id": "flow_low", "label": "1 - 5 cm/s (Low Drift)", "min": 1.0, "max": 5.0},
    {"id": "flow_medium", "label": "5 - 15 cm/s (Cabin Ventilation)", "min": 5.0, "max": 15.0},
    {"id": "flow_high", "label": "> 15 cm/s (High Flow/Blowoff)", "min": 15.0, "max": 200.0},
]

PRESSURE_BINS = [
    {"id": "p_hypobaric", "label": "< 70 kPa (Hypobaric Exploration)", "min": 0.0, "max": 70.0},
    {"id": "p_intermediate", "label": "70 - 95 kPa (Depressurized)", "min": 70.0, "max": 95.0},
    {"id": "p_normobaric", "label": "95 - 105 kPa (Sea Level/ISS)", "min": 95.0, "max": 105.0},
    {"id": "p_hyperbaric", "label": "> 105 kPa (Hyperbaric)", "min": 105.0, "max": 500.0},
]

TEAM_EXPERIMENT_PROPOSALS = [
    {
        "gap_id": "GAP_HYPOBARIC_HIGH_O2_HIGH_FLOW",
        "title": "Hypobaric high-oxygen, high-flow conditions",
        "regime": "Pressure < 60 kPa, Oxygen > 30%, Forced Flow > 15 cm/s",
        "materials_affected": ["Nomex", "Delrin", "Cotton"],
        "recommended_experiment": "Team proposal: compare these materials at 56.5 kPa, 34% oxygen and flows above 15 cm/s, subject to qualified experimental review.",
    },
    {
        "gap_id": "GAP_DELRIN_NOMEX_EXTINCTION_LIMIT",
        "title": "Delrin and Nomex at low imposed airflow",
        "regime": "Forced Flow < 1 cm/s, Oxygen >= 20.9%, Any Pressure",
        "materials_affected": ["Delrin", "Nomex"],
        "recommended_experiment": "Team proposal: measure Delrin and Nomex outcomes with controlled airflow ramps below 1 cm/s, documenting ignition history and sample geometry.",
    },
    {
        "gap_id": "GAP_THICK_SAMPLE_CONCURRENT_FLOW",
        "title": "Thick samples in concurrent flow",
        "regime": "Fuel Thickness > 5 mm, Concurrent Flow, All Atmospheres",
        "materials_affected": ["PMMA", "Polyethylene", "Delrin"],
        "recommended_experiment": "Team proposal: compare thick-sample concurrent-flow observations across oxygen conditions while controlling thickness and ignition protocol.",
    },
]


class ResearchCoverageEngine:
    """Computes indexed observation density and scoped proposal counts."""

    def __init__(self, data_path: Path = DATA_PATH):
        self.data_path = data_path
        self._load_dataset()

    def _load_dataset(self) -> None:
        if self.data_path.exists():
            self.df = pd.read_parquet(self.data_path)
        else:
            self.df = pd.DataFrame()

    def get_coverage_summary(self) -> dict[str, Any]:
        """Summarize indexed bins and count observations for team-selected proposals."""
        if self.df.empty:
            return {"total_experiments": 0, "status": "no_data"}

        total_experiments = len(self.df)
        materials = sorted(self.df["material"].dropna().unique().tolist())
        investigations = sorted(self.df["investigation"].dropna().unique().tolist())
        reports = sorted(self.df["report_id"].dropna().unique().tolist())

        # Material-level breakdown
        material_breakdown = {}
        for mat in materials:
            mdf = self.df[self.df["material"] == mat]
            outcomes = mdf["outcome"].value_counts().to_dict()
            material_breakdown[mat] = {
                "count": len(mdf),
                "pct_of_total": round(len(mdf) / total_experiments * 100, 1),
                "outcomes": {
                    "spread": int(outcomes.get("spread", 0)),
                    "marginal_spread": int(outcomes.get("marginal_spread", 0)),
                    "no_spread": int(outcomes.get("no_spread", 0)),
                },
                "oxygen_range": [float(mdf["oxygen_pct"].min()), float(mdf["oxygen_pct"].max())],
                "flow_range": [float(mdf["flow_cm_s"].min()), float(mdf["flow_cm_s"].max())],
                "pressure_range": [float(mdf["pressure_kpa"].min()), float(mdf["pressure_kpa"].max())],
            }

        # 2D Grid: Oxygen Bins vs. Flow Bins
        grid_cells = []
        for o2_b in O2_BINS:
            for fl_b in FLOW_BINS:
                mask = (
                    (self.df["oxygen_pct"] >= o2_b["min"])
                    & (self.df["oxygen_pct"] < o2_b["max"])
                    & (self.df["flow_cm_s"] >= fl_b["min"])
                    & (self.df["flow_cm_s"] < fl_b["max"])
                )
                cell_df = self.df[mask]
                count = len(cell_df)

                if count >= 10:
                    density = "HIGH"
                elif count >= 3:
                    density = "MODERATE"
                elif count >= 1:
                    density = "SPARSE"
                else:
                    density = "NO_INDEXED_OBSERVATIONS"

                cell_outcomes = cell_df["outcome"].value_counts().to_dict() if count > 0 else {}
                cell_mats = cell_df["material"].unique().tolist() if count > 0 else []

                grid_cells.append({
                    "o2_bin_id": o2_b["id"],
                    "o2_bin_label": o2_b["label"],
                    "flow_bin_id": fl_b["id"],
                    "flow_bin_label": fl_b["label"],
                    "count": count,
                    "density": density,
                    "materials": cell_mats,
                    "spread_count": int(cell_outcomes.get("spread", 0)),
                    "marginal_count": int(cell_outcomes.get("marginal_spread", 0)),
                    "no_spread_count": int(cell_outcomes.get("no_spread", 0)),
                })

        # Calculate matrix completeness
        total_cells = len(grid_cells)
        covered_cells = sum(1 for c in grid_cells if c["count"] > 0)
        high_cells = sum(1 for c in grid_cells if c["density"] == "HIGH")
        gap_cells = sum(1 for c in grid_cells if c["density"] == "NO_INDEXED_OBSERVATIONS")
        coverage_completeness_pct = round(covered_cells / total_cells * 100, 1)

        proposal_masks = [
            (self.df["pressure_kpa"] < 60) & (self.df["oxygen_pct"] > 30) & (self.df["flow_cm_s"] > 15),
            (self.df["flow_cm_s"] < 1) & (self.df["oxygen_pct"] >= 20.9),
            (self.df["sample_thickness_mm"] > 5) & (self.df["flow_direction"] == "concurrent"),
        ]
        proposals = []
        for proposal, mask in zip(TEAM_EXPERIMENT_PROPOSALS, proposal_masks):
            matching = self.df[mask & self.df["material"].isin(proposal["materials_affected"])]
            count = len(matching)
            proposals.append({
                **proposal,
                "status": "team_proposal",
                "scope": "current FLARE-X dataset only; not a literature-wide finding",
                "matching_observations": count,
                "material_counts": {mat: int((matching["material"] == mat).sum())
                                    for mat in proposal["materials_affected"]},
                "coverage_statement": (
                    "No matching observations in the current FLARE-X dataset" if count == 0 else
                    f"{count} matching observations in the current FLARE-X dataset"
                ),
                "scientific_rationale": "Team-selected comparison for further study; no claim that the wider literature lacks measurements. Missing context is not counted as a match.",
            })

        return {
            "scope": "current FLARE-X dataset",
            "coverage_basis": "Occupied oxygen-by-airflow bins, aggregated across materials, pressures, geometries and ignition protocols; not scientific completeness.",
            "total_verified_experiments": total_experiments,
            "unique_materials_tested": len(materials),
            "unique_investigations": len(investigations),
            "unique_nasa_reports": len(reports),
            "coverage_completeness_pct": coverage_completeness_pct,
            "matrix_dimensions": {
                "oxygen_bins": O2_BINS,
                "flow_bins": FLOW_BINS,
                "pressure_bins": PRESSURE_BINS,
            },
            "heatmap_grid": grid_cells,
            "material_breakdown": material_breakdown,
            "high_density_cells_count": high_cells,
            "untested_gap_cells_count": gap_cells,
            "empirical_white_spaces": proposals,
            "scientific_takeaway": (
                f"{covered_cells} of {total_cells} oxygen-by-airflow bins contain observations in the current "
                f"FLARE-X dataset. {gap_cells} bins have no matching observations in the current FLARE-X dataset. "
                "This map does not measure literature completeness, scientific reliability or safety. "
                "Suggested experiments are team proposals, not independently verified literature gaps."
            ),
        }
