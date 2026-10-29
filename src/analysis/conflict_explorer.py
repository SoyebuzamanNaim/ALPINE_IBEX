"""Scientific Evidence Conflict Explorer for FLARE-X Evidence Atlas.

Analyzes experimental comparability, dimensional discrepancies, and physical reconciliations
between disparate NASA microgravity combustion investigations (e.g. BASS-II, Saffire, SoFIE, Drop Tower).
Prevents misleading synthesis of fundamentally different physical regimes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
PROVENANCE_PATH = ROOT / "data" / "metadata" / "provenance_registry.json"
CORPUS_DIR = ROOT / "cache" / "report_corpus"

ComparabilityVerdict = Literal[
    "HIGHLY_COMPARABLE",
    "COMPLEMENTARY_DIFFERENT_REGIMES",
    "STRUCTURAL_MISMATCH_NON_COMPARABLE",
]


@dataclass
class DimensionComparison:
    dimension: str
    study_a_value: str
    study_b_value: str
    match_status: Literal["MATCH", "MODERATE_DIFFERENCE", "SEVERE_MISMATCH"]
    physical_impact: str


@dataclass
class ConflictAnalysisResult:
    study_a_id: str
    study_a_title: str
    study_b_id: str
    study_b_title: str
    comparability_score: float  # 0.0 to 1.0
    verdict: ComparabilityVerdict
    verdict_summary: str
    dimensions: list[dict[str, Any]]
    scientific_reconciliation: str
    key_physical_differences: list[str]
    cautionary_guidance: str
    citations: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "study_a_id": self.study_a_id,
            "study_a_title": self.study_a_title,
            "study_b_id": self.study_b_id,
            "study_b_title": self.study_b_title,
            "comparability_score": round(self.comparability_score, 2),
            "verdict": self.verdict,
            "verdict_summary": self.verdict_summary,
            "dimensions": self.dimensions,
            "scientific_reconciliation": self.scientific_reconciliation,
            "key_physical_differences": self.key_physical_differences,
            "cautionary_guidance": self.cautionary_guidance,
            "citations": self.citations,
        }


# Pre-defined canonical NASA study profiles for cross-study comparability
CANONICAL_STUDY_PROFILES: dict[str, dict[str, Any]] = {
    "BASS-II": {
        "title": "BASS-II (Burning and Suppression of Solids - II, ISS MSG)",
        "report_id": "20210011385",
        "citation": "NASA/TM-20210011385",
        "url": "https://ntrs.nasa.gov/citations/20210011385",
        "scale": "Centimeter-scale (1-2 cm wide, 10 cm long)",
        "chamber_volume_m3": 0.255,  # MSG working volume
        "duration": "Quasi-steady (up to 300 seconds continuous burn)",
        "thermal_regime": "Thermally thin to moderately thick (0.1 mm - 10 mm)",
        "flow_type": "Opposed forced flow (0.2 to 25 cm/s)",
        "atmosphere": "Standard normobaric (101.3 kPa, 17-21% O2)",
        "materials": ["PMMA", "Cotton", "Delrin", "Nomex"],
        "gravity": "Orbital microgravity (ISS ~10^-6 g)",
        "focus": "Fundamental flame spread velocity and low-flow extinction limits in enclosed duct",
    },
    "Saffire": {
        "title": "Saffire-I / Saffire-II (Spacecraft Fire Safety Experiment, Cygnus)",
        "report_id": "20170000230",
        "citation": "NASA/TM-20170000230 (Ruff & Urban, Saffire-I/II/III status)",
        "url": "https://ntrs.nasa.gov/citations/20170000230",
        "scale": "Vehicle-scale (0.4 m wide x 1.0 m long fabric, large flow tunnel)",
        "chamber_volume_m3": 18.0,  # Cygnus pressurized cargo module
        "duration": "Full combustion burn (hundreds of seconds until consumption or suppression)",
        "thermal_regime": "Thick fabric blends (Sibal cloth: 75% cotton / 25% fiberglass, PMMA slabs)",
        "flow_type": "Concurrent and opposed forced cabin ventilation (10 to 30 cm/s)",
        "atmosphere": "Standard to hypoxic / enriched spaceflight atmospheres (101 kPa, 21% O2 down to low O2)",
        "materials": ["Cotton", "PMMA", "Nomex"],
        "gravity": "Orbital microgravity (Cygnus cargo vehicle ~10^-6 g)",
        "focus": "Realistic spacecraft material flammability, flame spread rate, and smoke detection at practical compartment scale",
    },
    "Drop_Tower_Olson": {
        "title": "NASA GRC Microgravity Opposed-Flow Extinction Study (Ferkul, 1989)",
        "report_id": "19890014267",
        "citation": "NASA CR-182264 (P. V. Ferkul, 1989)",
        "url": "https://ntrs.nasa.gov/citations/19890014267",
        "scale": "Small test strip (1 cm wide, 5 cm long)",
        "chamber_volume_m3": 0.04,
        "duration": "Strictly transient (5.18 seconds freefall)",
        "thermal_regime": "Thermally thin cast cellulose and thin PMMA films (<= 0.2 mm)",
        "flow_type": "Opposed forced flow (1 to 20 cm/s)",
        "atmosphere": "Normobaric air and O2/N2 blends (101.3 kPa, 15-21% O2)",
        "materials": ["PMMA", "Cellulose"],
        "gravity": "Terrestrial drop tower (~10^-4 g for 5.18 s)",
        "focus": "Transient opposed-flow diffusion flame extinction limits and extinction boundary mapping",
    },
    "Exploration_Atmospheres": {
        "title": "Microgravity Flame Spread in Exploration Atmospheres (NASA GRC)",
        "report_id": "20080034883",
        "citation": "NASA/TM-20080034883 (Olson, Ruff & Miller)",
        "url": "https://ntrs.nasa.gov/citations/20080034883",
        "scale": "Thin-fuel samples in a low-speed flow tunnel simulating cabin ventilation",
        "chamber_volume_m3": 0.5,
        "duration": "Up to 120 seconds",
        "thermal_regime": "Thin films and papers (Ultem 1000, Nomex HT90-40, Mylar G, Kimwipes)",
        "flow_type": "Opposed and concurrent low-speed forced flow",
        "atmosphere": "Variable pressure and oxygen spanning exploration atmospheres",
        "materials": ["Nomex", "Cellulose"],
        "gravity": "Microgravity flow tunnel, compared against 1-g NASA-STD-6001 Test 1",
        "focus": "1-g screening under-predicts 0-g flammability: measured ULOI/MOC are up to 4% O2 mole fraction higher in 1-g than in 0-g",
    },
    "SoFIE_MIST": {
        "title": "SoFIE-MIST (Solid Fuel Ignition and Extinction - Material Ignition and Spread Test)",
        "report_id": "20200000361",
        "citation": "NASA/TM-20200000361 (SoFIE Project on ISS)",
        "url": "https://ntrs.nasa.gov/citations/20200000361",
        "scale": "Narrow flow duct (cylindrical sample rods and flat strips 1-2 cm)",
        "chamber_volume_m3": 0.1,  # Combustion Integrated Rack (CIR) chamber
        "duration": "Extended steady-state (tens of minutes in CIR)",
        "thermal_regime": "Controlled thickness rods and sheets (PMMA, POM)",
        "flow_type": "Opposed and concurrent axial duct flow (0 to 20 cm/s)",
        "atmosphere": "Variable pressure (50 to 100 kPa) and variable O2 (15 to 35%)",
        "materials": ["PMMA", "Delrin"],
        "gravity": "ISS Combustion Integrated Rack (~10^-6 g)",
        "focus": "Microgravity ignition delays, flame spread, and radiation-induced radiative extinction boundaries",
    },
}

# Pre-packaged case studies demonstrating critical research conflicts
CANONICAL_CONFLICT_CASES = [
    {
        "case_id": "bass2_vs_saffire",
        "name": "BASS-II (Glovebox Microscale) vs. Saffire (Cygnus Vehicle-Scale)",
        "study_a": "BASS-II",
        "study_b": "Saffire",
        "core_conflict": "Apparent discrepancy in flame extinction limits and spread sustained at low flow velocities",
    },
    {
        "case_id": "drop_tower_vs_bass2",
        "name": "5.18s Drop Tower (Olson CR-182264) vs. BASS-II (ISS Long Duration)",
        "study_a": "Drop_Tower_Olson",
        "study_b": "BASS-II",
        "core_conflict": "Transient extinction boundaries vs. steady-state radiative quenching limits",
    },
    {
        "case_id": "normobaric_vs_exploration",
        "name": "Standard Sea-Level (101.3 kPa, 21% O2) vs. Exploration Atmosphere (56.5 kPa, 34% O2)",
        "study_a": "BASS-II",
        "study_b": "Exploration_Atmospheres",
        "core_conflict": "Chemical kinetic enhancement from elevated O2 vs. decreased heat capacity and Reynolds number under hypobaric pressure",
    },
    {
        "case_id": "sofie_vs_drop_tower",
        "name": "SoFIE-MIST (CIR Extended Chamber) vs. 5.18s Drop Tower",
        "study_a": "SoFIE_MIST",
        "study_b": "Drop_Tower_Olson",
        "core_conflict": "Radiative loss accumulation over long burn durations causing low-speed quenching not visible in 5.18s drop windows",
    },
]


class ConflictExplorerEngine:
    """Core analysis engine for detecting experimental comparability conflicts."""

    def __init__(self, data_path: Path = DATA_PATH, provenance_path: Path = PROVENANCE_PATH):
        self.data_path = data_path
        self.provenance_path = provenance_path
        self._load_data()

    def _load_data(self) -> None:
        if self.data_path.exists():
            self.df = pd.read_parquet(self.data_path)
        else:
            self.df = pd.DataFrame()

        self.provenance: dict[str, dict[str, Any]] = {}
        if self.provenance_path.exists():
            try:
                raw = json.loads(self.provenance_path.read_bytes())
                if isinstance(raw, list):
                    for item in raw:
                        self.provenance[item["experiment_id"]] = item
                elif isinstance(raw, dict):
                    self.provenance = raw
            except Exception:
                pass

    def list_canonical_cases(self) -> list[dict[str, Any]]:
        """List pre-configured canonical conflict case studies."""
        return CANONICAL_CONFLICT_CASES

    def list_study_profiles(self) -> dict[str, Any]:
        """List available canonical study profiles for comparison."""
        return {
            k: {
                "key": k,
                "title": v["title"],
                "report_id": v["report_id"],
                "citation": v["citation"],
                "scale": v["scale"],
                "flow_type": v["flow_type"],
                "atmosphere": v["atmosphere"],
                "materials": v["materials"],
            }
            for k, v in CANONICAL_STUDY_PROFILES.items()
        }

    def compare_canonical_studies(self, key_a: str, key_b: str) -> dict[str, Any]:
        """Perform deep physical comparability analysis between two canonical study profiles."""
        if key_a not in CANONICAL_STUDY_PROFILES:
            raise ValueError(f"Unknown study profile '{key_a}'. Available: {list(CANONICAL_STUDY_PROFILES.keys())}")
        if key_b not in CANONICAL_STUDY_PROFILES:
            raise ValueError(f"Unknown study profile '{key_b}'. Available: {list(CANONICAL_STUDY_PROFILES.keys())}")

        prof_a = CANONICAL_STUDY_PROFILES[key_a]
        prof_b = CANONICAL_STUDY_PROFILES[key_b]

        dimensions: list[dict[str, Any]] = []
        score_penalty = 0.0
        key_differences = []

        # 1. Physical Scale & Enclosure Dimension
        if key_a == key_b:
            scale_status = "MATCH"
            scale_impact = "Identical experimental geometries."
        elif "Centimeter" in prof_a["scale"] and "Vehicle-scale" in prof_b["scale"]:
            scale_status = "SEVERE_MISMATCH"
            scale_impact = (
                "Massive scale divergence (0.01 m vs 1.0 m). Saffire operates in a large Cygnus module (18 m^3) "
                "with significant radiant feedback and turbulent plume formation, while BASS-II is confined to a 0.25 m^3 "
                "duct where laminar boundary layers and cold wall quenching dominate."
            )
            score_penalty += 0.35
            key_differences.append("Sample and enclosure scale difference alters radiant feedback and boundary layer thickness")
        elif "Drop Tower" in prof_a["title"] or "Drop Tower" in prof_b["title"]:
            scale_status = "MODERATE_DIFFERENCE"
            scale_impact = (
                "Rig enclosure differences. Drop tower rigs feature compact chambers to fit within drop frames, "
                "yielding faster gas-phase accumulation than orbital rigs."
            )
            score_penalty += 0.15
            key_differences.append("Rig confinement and chamber volume differences")
        else:
            scale_status = "MATCH"
            scale_impact = "Comparable laboratory flow duct geometry."

        dimensions.append({
            "dimension": "Enclosure Scale & Sample Dimensions",
            "study_a": prof_a["scale"],
            "study_b": prof_b["scale"],
            "status": scale_status,
            "physical_impact": scale_impact,
        })

        # 2. Duration & Steady-State Criterion
        if "5.18 seconds" in prof_a["duration"] or "5.18 seconds" in prof_b["duration"]:
            dur_status = "SEVERE_MISMATCH"
            dur_impact = (
                "Transient vs. Quasi-Steady condition. 5.18 seconds is insufficient for solid fuels with thickness > 0.2 mm "
                "to establish a thermal steady-state conduction profile (thermal penetration time t_th ~ L_th^2 / alpha > 10 s). "
                "Apparent extinction limits from drop towers reflect ignition transient decay rather than true steady quenching."
            )
            score_penalty += 0.30
            key_differences.append("Transient 5.18-second drop exposure vs long-duration steady orbital burn")
        else:
            dur_status = "MATCH"
            dur_impact = "Both investigations allow quasi-steady thermal equilibrium (> 60s burn duration)."

        dimensions.append({
            "dimension": "Test Duration & Thermal Steady-State",
            "study_a": prof_a["duration"],
            "study_b": prof_b["duration"],
            "status": dur_status,
            "physical_impact": dur_impact,
        })

        # 3. Flow Regime & Aerodynamics
        if prof_a["flow_type"] != prof_b["flow_type"]:
            flow_status = "MODERATE_DIFFERENCE"
            flow_impact = (
                f"Aerodynamic configuration mismatch: '{prof_a['flow_type']}' vs '{prof_b['flow_type']}'. "
                "Concurrent flow pre-heats virgin material ahead of the pyrolysis zone, dramatically extending "
                "flammability boundaries compared to opposed flow where heat is carried away from the unburnt solid."
            )
            score_penalty += 0.20
            key_differences.append("Opposed vs concurrent convection flow aerodynamics")
        else:
            flow_status = "MATCH"
            flow_impact = "Matching convection flow direction and velocity ranges."

        dimensions.append({
            "dimension": "Convection Flow Direction & Aerodynamics",
            "study_a": prof_a["flow_type"],
            "study_b": prof_b["flow_type"],
            "status": flow_status,
            "physical_impact": flow_impact,
        })

        # 4. Atmospheric Pressure & Oxygen Environment
        if "Hypobaric" in prof_a["atmosphere"] or "Hypobaric" in prof_b["atmosphere"]:
            atm_status = "SEVERE_MISMATCH"
            atm_impact = (
                "Atmospheric regime shift (Hypobaric 56 kPa / 34% O2 vs Normobaric 101.3 kPa / 21% O2). "
                "Reduced pressure increases mass diffusivity (D ~ P^-1) and lowers gas phase heat capacity, while elevated O2 "
                "enhances flame temperature. The combined Damköhler number shifts non-linearly."
            )
            score_penalty += 0.25
            key_differences.append("Hypobaric exploration atmosphere (56 kPa) vs sea-level pressure (101 kPa)")
        else:
            atm_status = "MATCH"
            atm_impact = "Compatible atmospheric pressure and oxygen partial pressures."

        dimensions.append({
            "dimension": "Atmospheric Pressure & Gas Chemistry",
            "study_a": prof_a["atmosphere"],
            "study_b": prof_b["atmosphere"],
            "status": atm_status,
            "physical_impact": atm_impact,
        })

        # Compute Final Score and Verdict
        comparability_score = max(0.1, round(1.0 - score_penalty, 2))
        if comparability_score >= 0.80:
            verdict: ComparabilityVerdict = "HIGHLY_COMPARABLE"
            verdict_summary = (
                "Studies share equivalent physical scales, steady-state durations, and aerodynamic flow regimes. "
                "Data points and flammability boundaries can be directly synthesized and quantitatively cross-validated."
            )
            cautionary_guidance = "Safe for combined numerical modeling and cross-experiment training."
        elif comparability_score >= 0.45:
            verdict = "COMPLEMENTARY_DIFFERENT_REGIMES"
            verdict_summary = (
                "Studies investigate distinct but complementary regimes of spacecraft fire safety. "
                "Differences in scale, flow direction, or pressure prevent direct numerical pooling, but comparing them "
                "provides vital boundary envelope insights."
            )
            cautionary_guidance = (
                "Do NOT aggregate numerical measurements directly into a single unstratified regression model. "
                "Treat as multi-regime bounding data and stratify predictions by investigation scale."
            )
        else:
            verdict = "STRUCTURAL_MISMATCH_NON_COMPARABLE"
            verdict_summary = (
                "Severe physical regime divergence (e.g. transient drop tower vs orbital vehicle scale, or hypobaric vs normobaric). "
                "Contradictions in observed flame spread rates or extinction limits are driven by physical regime differences, "
                "not measurement error."
            )
            cautionary_guidance = (
                "Combining these datasets without non-dimensional scaling (Biot, Damköhler, Reynolds numbers) "
                "will produce erroneous ML predictions and false safety margins."
            )

        # Build Scientific Reconciliation text
        scientific_reconciliation = self._generate_reconciliation(key_a, key_b, prof_a, prof_b, verdict)

        citations = {
            "study_a": {
                "name": prof_a["title"],
                "report_id": prof_a["report_id"],
                "citation": prof_a["citation"],
                "url": prof_a["url"],
            },
            "study_b": {
                "name": prof_b["title"],
                "report_id": prof_b["report_id"],
                "citation": prof_b["citation"],
                "url": prof_b["url"],
            },
        }

        return ConflictAnalysisResult(
            study_a_id=key_a,
            study_a_title=prof_a["title"],
            study_b_id=key_b,
            study_b_title=prof_b["title"],
            comparability_score=comparability_score,
            verdict=verdict,
            verdict_summary=verdict_summary,
            dimensions=dimensions,
            scientific_reconciliation=scientific_reconciliation,
            key_physical_differences=key_differences,
            cautionary_guidance=cautionary_guidance,
            citations=citations,
        ).to_dict()

    def compare_experiments(self, exp_id_a: str, exp_id_b: str) -> dict[str, Any]:
        """Compare two specific historical experiment points from the dataset."""
        if self.df.empty:
            raise RuntimeError("Authoritative experiments dataset not loaded.")

        row_a = self.df[self.df["experiment_id"] == exp_id_a]
        row_b = self.df[self.df["experiment_id"] == exp_id_b]

        if row_a.empty:
            raise ValueError(f"Experiment '{exp_id_a}' not found in dataset.")
        if row_b.empty:
            raise ValueError(f"Experiment '{exp_id_b}' not found in dataset.")

        rec_a = row_a.iloc[0].to_dict()
        rec_b = row_b.iloc[0].to_dict()

        dimensions: list[dict[str, Any]] = []
        score_penalty = 0.0
        key_differences = []

        # Material
        if rec_a["material"] != rec_b["material"]:
            dimensions.append({
                "dimension": "Fuel Material Chemistry",
                "study_a": rec_a["material"],
                "study_b": rec_b["material"],
                "status": "SEVERE_MISMATCH",
                "physical_impact": f"Different chemical pyrolysis mechanisms and heats of combustion ({rec_a['material']} vs {rec_b['material']}).",
            })
            score_penalty += 0.4
            key_differences.append(f"Material difference ({rec_a['material']} vs {rec_b['material']})")
        else:
            dimensions.append({
                "dimension": "Fuel Material Chemistry",
                "study_a": rec_a["material"],
                "study_b": rec_b["material"],
                "status": "MATCH",
                "physical_impact": f"Identical polymer fuel base ({rec_a['material']}).",
            })

        # Oxygen
        o2_diff = abs(float(rec_a["oxygen_pct"]) - float(rec_b["oxygen_pct"]))
        if o2_diff > 4.0:
            dimensions.append({
                "dimension": "Ambient Oxygen Concentration",
                "study_a": f"{rec_a['oxygen_pct']}% O2",
                "study_b": f"{rec_b['oxygen_pct']}% O2",
                "status": "SEVERE_MISMATCH",
                "physical_impact": f"Large delta of {o2_diff:.1f}% O2 alters adiabatic flame temperature significantly.",
            })
            score_penalty += 0.25
            key_differences.append(f"Oxygen concentration difference ({o2_diff:.1f}% O2)")
        elif o2_diff > 1.0:
            dimensions.append({
                "dimension": "Ambient Oxygen Concentration",
                "study_a": f"{rec_a['oxygen_pct']}% O2",
                "study_b": f"{rec_b['oxygen_pct']}% O2",
                "status": "MODERATE_DIFFERENCE",
                "physical_impact": f"Moderate delta of {o2_diff:.1f}% O2.",
            })
            score_penalty += 0.1
        else:
            dimensions.append({
                "dimension": "Ambient Oxygen Concentration",
                "study_a": f"{rec_a['oxygen_pct']}% O2",
                "study_b": f"{rec_b['oxygen_pct']}% O2",
                "status": "MATCH",
                "physical_impact": "Closely matched oxygen levels.",
            })

        # Flow
        flow_diff = abs(float(rec_a["flow_cm_s"]) - float(rec_b["flow_cm_s"]))
        if flow_diff > 5.0:
            dimensions.append({
                "dimension": "Forced Convection Velocity",
                "study_a": f"{rec_a['flow_cm_s']} cm/s",
                "study_b": f"{rec_b['flow_cm_s']} cm/s",
                "status": "SEVERE_MISMATCH",
                "physical_impact": f"Flow velocity difference of {flow_diff:.1f} cm/s shifts boundary layer thickness and Damköhler number.",
            })
            score_penalty += 0.2
            key_differences.append(f"Flow velocity difference ({flow_diff:.1f} cm/s)")
        else:
            dimensions.append({
                "dimension": "Forced Convection Velocity",
                "study_a": f"{rec_a['flow_cm_s']} cm/s",
                "study_b": f"{rec_b['flow_cm_s']} cm/s",
                "status": "MATCH",
                "physical_impact": "Similar forced convection velocities.",
            })

        # Pressure
        p_diff = abs(float(rec_a["pressure_kpa"]) - float(rec_b["pressure_kpa"]))
        if p_diff > 10.0:
            dimensions.append({
                "dimension": "Ambient Pressure",
                "study_a": f"{rec_a['pressure_kpa']} kPa",
                "study_b": f"{rec_b['pressure_kpa']} kPa",
                "status": "SEVERE_MISMATCH",
                "physical_impact": f"Pressure difference of {p_diff:.1f} kPa alters gas density and molecular diffusion rates.",
            })
            score_penalty += 0.2
            key_differences.append(f"Pressure disparity ({p_diff:.1f} kPa)")
        else:
            dimensions.append({
                "dimension": "Ambient Pressure",
                "study_a": f"{rec_a['pressure_kpa']} kPa",
                "study_b": f"{rec_b['pressure_kpa']} kPa",
                "status": "MATCH",
                "physical_impact": "Matched ambient pressures.",
            })

        # Outcomes comparison
        outcome_a = rec_a.get("outcome")
        outcome_b = rec_b.get("outcome")
        outcome_conflict = outcome_a != outcome_b

        score = max(0.1, round(1.0 - score_penalty, 2))
        if score >= 0.8:
            verdict: ComparabilityVerdict = "HIGHLY_COMPARABLE"
            if outcome_conflict:
                reconciliation = (
                    f"Direct flammability discrepancy: {exp_id_a} resulted in '{outcome_a}' whereas "
                    f"{exp_id_b} resulted in '{outcome_b}' despite similar conditions. This highlights sensitivity near the "
                    "flammability regime boundary, likely driven by sample thickness or ignition energy."
                )
            else:
                reconciliation = f"Both tests consistently confirm the '{outcome_a}' regime under closely matched parameters."
        elif score >= 0.45:
            verdict = "COMPLEMENTARY_DIFFERENT_REGIMES"
            reconciliation = (
                f"The difference in observed outcomes ('{outcome_a}' vs '{outcome_b}') is physically justified by the "
                f"differing experimental parameters: {', '.join(key_differences)}."
            )
        else:
            verdict = "STRUCTURAL_MISMATCH_NON_COMPARABLE"
            reconciliation = (
                f"Experiments represent fundamentally different test regimes ({', '.join(key_differences)}). "
                "Any apparent conflict in outcomes cannot be treated as contradictory scientific evidence."
            )

        prov_a = self.provenance.get(exp_id_a, {})
        prov_b = self.provenance.get(exp_id_b, {})

        citations = {
            "study_a": {
                "experiment_id": exp_id_a,
                "report_id": rec_a["report_id"],
                "citation": prov_a.get("exact_source_citation", rec_a.get("source_url", "")),
                "url": rec_a["source_url"],
                "tier": prov_a.get("verification_tier", "VERIFIED_FLIGHT_TABLE"),
            },
            "study_b": {
                "experiment_id": exp_id_b,
                "report_id": rec_b["report_id"],
                "citation": prov_b.get("exact_source_citation", rec_b.get("source_url", "")),
                "url": rec_b["source_url"],
                "tier": prov_b.get("verification_tier", "VERIFIED_FLIGHT_TABLE"),
            },
        }

        return ConflictAnalysisResult(
            study_a_id=exp_id_a,
            study_a_title=f"Test {exp_id_a} ({rec_a['material']}, {rec_a['oxygen_pct']}% O2, {rec_a['flow_cm_s']} cm/s -> {outcome_a})",
            study_b_id=exp_id_b,
            study_b_title=f"Test {exp_id_b} ({rec_b['material']}, {rec_b['oxygen_pct']}% O2, {rec_b['flow_cm_s']} cm/s -> {outcome_b})",
            comparability_score=score,
            verdict=verdict,
            verdict_summary=f"Comparability score {score:.2f}: {verdict.replace('_', ' ')}",
            dimensions=dimensions,
            scientific_reconciliation=reconciliation,
            key_physical_differences=key_differences,
            cautionary_guidance="Inspect exact source citations and sample thicknesses before asserting scientific conflict.",
            citations=citations,
        ).to_dict()

    def _generate_reconciliation(
        self,
        key_a: str,
        key_b: str,
        prof_a: dict[str, Any],
        prof_b: dict[str, Any],
        verdict: ComparabilityVerdict,
    ) -> str:
        """Generate authoritative physical narrative reconciling experimental differences."""
        if {key_a, key_b} == {"BASS-II", "Saffire"}:
            return (
                "BASS-II was designed to examine fundamental microgravity flame spread on 1–2 cm wide solid samples inside "
                "the enclosed Microgravity Science Glovebox (0.25 m^3). In contrast, Saffire tests meter-scale fabrics (0.4 m x 1.0 m) "
                "inside an uncrewed Cygnus cargo spacecraft (18 m^3). Because Saffire's large sample generates substantial convective "
                "heat release and luminous flame volume, flame radiation back to the fuel surface supports sustained flame spread even "
                "under ventilation flows where centimeter-scale BASS-II samples suffer radiative extinction. Thus, Saffire's broader "
                "flammability envelope does not contradict BASS-II; rather, it demonstrates that radiative scaling and enclosure "
                "capacitance dictate real spacecraft-scale fire growth."
            )
        elif {key_a, key_b} == {"Drop_Tower_Olson", "BASS-II"}:
            return (
                "The NASA GRC 5.18-second drop tower experiments (Olson CR-182264 / Bhattacharjee AIAA-2004-0968) captured pioneering "
                "extinction boundaries. However, 5.18 seconds is shorter than the characteristic solid thermal diffusion time for "
                "fuels thicker than 0.2 mm (t_diff = L^2 / alpha > 10 s). Consequently, flames in drop towers may appear to extinguish "
                "due to insufficient ignition transient recovery. Orbital tests aboard the ISS (BASS-II) allowed steady burns exceeding "
                "200 seconds, revealing that low-flow extinction is governed by radiative heat loss accumulation from the gas phase flame, "
                "a steady-state phenomenon that requires tens of seconds to manifest."
            )
        elif {key_a, key_b} == {"BASS-II", "Exploration_Atmospheres"}:
            return (
                "Standard NASA flammability characterization (BASS-II, NASA-STD-6001 Test 1) is grounded in normobaric air "
                "(101.3 kPa, 21% O2). NASA Exploration Atmospheres (e.g. Orion and Gateway cabin environments: 56.5 kPa / 34% O2) "
                "operate under hypobaric conditions to reduce spacewalk prebreathe duration while maintaining oxygen partial pressure. "
                "While higher O2 mole fraction increases flame temperatures and reaction rates, lower ambient pressure increases molecular "
                "diffusivities and decreases buoyant and forced convection Reynolds numbers. Consequently, flammability ranking and "
                "extinction boundary slopes measured at 101 kPa cannot be linearly mapped to exploration conditions without accounting "
                "for the pressure dependence of gas-phase kinetics."
            )
        elif {key_a, key_b} == {"SoFIE_MIST", "Drop_Tower_Olson"}:
            return (
                "SoFIE-MIST aboard the ISS Combustion Integrated Rack provides long-duration microgravity environments with precise "
                "axial flow control, enabling measurements of both the high-flow blowoff extinction limit and the low-flow radiative "
                "quenching limit. Drop tower experiments could only reliably capture the high-flow blowoff boundary because the 5.18s "
                "window terminated before radiative heat losses could suppress low-flow flame spread. SoFIE confirms the U-shaped "
                "flammability boundary predicted by theory, whereas drop tower data captured only the left-hand branch."
            )
        else:
            return (
                f"Comparison between {prof_a['title']} and {prof_b['title']} reveals differences across "
                f"scale, flow aerodynamics, and chamber pressure. These structural differences explain discrepancies in reported "
                "spread rates and extinction thresholds. Microgravity fire safety models must avoid unstratified pooling of these data."
            )
