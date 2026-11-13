"""FastAPI Application for FLARE-X Flammability Explorer.

Exposes predictive models, experimental envelope guardrails, nearest-experiment
citations, counterfactual sweeps, and 2-D decision boundary slices.
"""
from __future__ import annotations

import csv
import json
import logging
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Path as PathParam, Query
from fastapi.middleware.cors import CORSMiddleware

from src.agents.interpreter import ScenarioInterpreter
from src.agents.orchestrator import AgentOrchestrator
from src.analysis.conflict_explorer import ConflictExplorerEngine
from src.analysis.coverage_map import ResearchCoverageEngine
from src.analysis.provenance_service import ProvenanceService
from src.api.schemas import (
    ConflictExperimentsRequest,
    ConflictStudiesRequest,
    CounterfactualRequest,
    ParseRequest,
    PredictRequest,
    PredictResponse,
    SweepRequest,
)
from src.api.middleware import RequestGuardMiddleware
from src.features.counterfactual import CounterfactualEngine
from src.retrieval.corpus_search import ReportCorpusSearcher
from src.retrieval.engine import EvidenceRetrievalEngine
from src.models.baseline import research_model_readiness

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flare_x_api")

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
MODEL_PATH = ROOT / "models" / "flame_spread_gb.joblib"
META_PATH = ROOT / "models" / "model_meta.json"
CORPUS_DIR = ROOT / "cache" / "report_corpus"
CATALOG_PATH = ROOT / "data" / "metadata" / "dataset_catalog.csv"

app = FastAPI(
    title="FLARE-X Microgravity Flammability API",
    description=(
        "Research prototype for exploring NASA microgravity combustion evidence "
        "and guarded flame-spread model results."
    ),
    version="1.0.0",
)
app.add_middleware(RequestGuardMiddleware)

# Enable CORS for local dev and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core engine instances
try:
    orchestrator = AgentOrchestrator(meta_path=META_PATH, data_path=DATA_PATH)
    cf_engine = CounterfactualEngine(data_path=DATA_PATH, meta_path=META_PATH)
except (FileNotFoundError, ValueError, KeyError) as exc:
    logger.warning("Optional research model unavailable: %s", exc)
    orchestrator = None
    cf_engine = None
evidence_engine = EvidenceRetrievalEngine()
interpreter = ScenarioInterpreter()
corpus_searcher = ReportCorpusSearcher(corpus_dir=CORPUS_DIR)
conflict_engine = ConflictExplorerEngine(data_path=DATA_PATH)
coverage_engine = ResearchCoverageEngine(data_path=DATA_PATH)
provenance_service = ProvenanceService(data_path=DATA_PATH, corpus_dir=CORPUS_DIR)


def _model_readiness() -> tuple[bool, str]:
    """Gate public inference on the measured report-grouped baseline comparison."""
    if orchestrator is None:
        return False, "Research model artifacts are unavailable or invalid; evidence retrieval remains available."
    return research_model_readiness(orchestrator.router.meta, DATA_PATH, MODEL_PATH)


def _require_model_ready() -> None:
    ready, reason = _model_readiness()
    if not ready:
        raise HTTPException(status_code=503, detail=reason)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    """Service health check, dataset status, and model readiness."""
    df = evidence_engine.nearest_retriever.df
    meta = orchestrator.router.meta if orchestrator is not None else {}
    model_ready, model_reason = _model_readiness()
    return {
        "status": "healthy" if model_ready else "degraded",
        "model_ready": model_ready,
        "evidence_ready": True,
        "model_readiness_reason": model_reason,
        "service": "FLARE-X Microgravity Flammability Engine",
        "version": "1.0.0",
        "dataset_rows": len(df),
        "dataset_sha256": evidence_engine.dataset_sha256,
        "model_type": meta.get("type"),
        "cv_accuracy": meta.get("cv_accuracy"),
        "release_mode": meta.get("release_mode"),
        "validation_status": meta.get("validation_status"),
        "nested_search": meta.get("nested_search"),
        "allowed_materials": sorted(df["material"].dropna().unique().tolist()),
    }


@app.post("/evidence", tags=["Evidence"])
def retrieve_evidence(request: PredictRequest) -> dict[str, Any]:
    """Retrieve indexed observations and cited summaries without running a classifier."""
    return evidence_engine.retrieve_evidence(**request.model_dump())


@app.get("/reports/search", tags=["Evidence"])
def search_reports(query: str = Query(min_length=1, max_length=500), limit: int = Query(5, ge=1, le=20)) -> dict[str, Any]:
    """Search indexed report titles, abstracts and keywords using lexical relevance."""
    reports = corpus_searcher.search(query, top_k=limit)
    return {"query": query, "ranking": "BM25 lexical relevance; not scientific reliability", "reports": reports}


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict(request: PredictRequest) -> dict[str, Any]:
    """Predict flammability regime and return nearest experimental citations.

    Conforms strictly to Section 7 API contract.
    If conditions fall outside empirical spaceflight bounds, prediction is refused
    with detailed reasons while still returning the nearest historical experiments.
    """
    payload = request.model_dump()
    if orchestrator is None:
        raise HTTPException(status_code=503, detail=_model_readiness()[1])
    model_ready, model_reason = _model_readiness()
    if not model_ready:
        envelope = orchestrator.guard.check(**payload)
        if envelope["in_training_range"] and not envelope.get("requires_abstention"):
            return {
                "inputs": payload,
                "in_training_range": True,
                "out_of_range_reasons": [],
                "status": "model_unvalidated",
                "prediction": None,
                "probabilities": None,
                "model": orchestrator.router.get_model_metadata(),
                "nearest_experiments": envelope["nearest_experiments"],
                "explanation": model_reason,
                "explanation_source": "model_validation_refusal",
                "warning_message": model_reason,
                "sparse_region_warning": envelope.get("sparse_region_warning", False),
                "knn_mean_distance": envelope.get("knn_mean_distance"),
                "model_ready": False,
            }
    res = orchestrator.run(payload)
    res["model_ready"] = model_ready
    if res.get("prediction") is not None:
        res["warning_message"] = " ".join(filter(None, (
            res.get("warning_message"), orchestrator.router.meta.get("research_warning"),
        )))
    return res


@app.get("/experiments", tags=["Data"])
def list_experiments(
    material: str | None = Query(None, max_length=64, description="Filter by solid fuel material"),
    limit: int = Query(200, ge=1, le=1000, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Row offset for pagination"),
) -> dict[str, Any]:
    """Retrieve verified NASA microgravity experiment observations."""
    df = pd.read_parquet(DATA_PATH)
    if material:
        df = df[df["material"].str.lower() == material.lower()]

    total = len(df)
    subset = df.iloc[offset : offset + limit]
    records = subset.to_dict(orient="records")

    # Replace NaN values with None for clean JSON serialization
    clean_records = []
    for r in records:
        clean_records.append({k: (None if pd.isna(v) else v) for k, v in r.items()})

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "experiments": clean_records,
    }


@app.get("/model", tags=["Model"])
def get_model_info() -> dict[str, Any]:
    """Return trained model metadata, CV evaluation metrics, confusion matrix, and training ranges."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail=_model_readiness()[1])
    return orchestrator.router.meta


def _mask_conflicting_grid_points(
    oxygen: np.ndarray,
    flow: np.ndarray,
    *,
    material: str,
    pressure_kpa: float,
    valid_mask: np.ndarray,
) -> np.ndarray:
    """Hide grid cells with opposite observed outcomes at identical model inputs."""
    mask = valid_mask.copy()
    for observed_o2, observed_pressure, observed_flow, observed_material in cf_engine.guard.conflicting_conditions:
        if observed_material != material or not math.isclose(observed_pressure, pressure_kpa, abs_tol=1e-6):
            continue
        mask &= ~(
            np.isclose(oxygen, observed_o2, rtol=0, atol=1e-6)
            & np.isclose(flow, observed_flow, rtol=0, atol=1e-6)
        )
    return mask


def _mask_joint_domain_grid_points(
    oxygen: np.ndarray,
    flow: np.ndarray,
    *,
    material: str,
    pressure_kpa: float,
    valid_mask: np.ndarray,
) -> np.ndarray:
    """Do not color model predictions outside the material's joint test domain."""
    mask = valid_mask.copy()
    if cf_engine.guard.distinct_condition_counts[material] < 3:
        return np.zeros_like(mask, dtype=bool)
    domain = cf_engine.guard.joint_domains[material]
    for index in np.flatnonzero(mask):
        mask[index] = domain.contains([oxygen[index], pressure_kpa, flow[index]])
    return mask


@app.get("/boundary", tags=["Visualizations"])
def get_decision_boundary(
    material: str = Query("PMMA", min_length=1, max_length=64, description="Material to slice"),
    pressure_kpa: float = Query(101.3, ge=0, le=200, allow_inf_nan=False, description="Fixed cabin pressure in kPa"),
    o2_steps: int = Query(25, ge=10, le=50, description="Oxygen grid resolution"),
    flow_steps: int = Query(25, ge=10, le=50, description="Flow grid resolution"),
) -> dict[str, Any]:
    """Compute a 2-D decision boundary slice over (oxygen_pct x flow_cm_s).

    Includes real experiments projected onto the 2-D slice for overlay plotting.
    """
    _require_model_ready()
    meta = json.loads(META_PATH.read_bytes())
    t_range = meta["training_range"]

    if material not in t_range["allowed_materials"]:
        raise HTTPException(
            status_code=400,
            detail=f"Material '{material}' not supported. Allowed: {t_range['allowed_materials']}",
        )

    mat_cfg = t_range.get("per_material", {}).get(material, {})
    o2_min = mat_cfg.get("oxygen_pct", {}).get("min", t_range["oxygen_pct"]["min"])
    o2_max = mat_cfg.get("oxygen_pct", {}).get("max", t_range["oxygen_pct"]["max"])
    f_min = mat_cfg.get("flow_cm_s", {}).get("min", t_range["flow_cm_s"]["min"])
    f_max = mat_cfg.get("flow_cm_s", {}).get("max", t_range["flow_cm_s"]["max"])

    # A single recorded condition still needs finite axes; the guard masks unsupported cells.
    display_o2 = [o2_min, o2_max] if o2_min != o2_max else [max(0., o2_min - .5), min(100., o2_max + .5)]
    display_flow = [f_min, f_max] if f_min != f_max else [max(0., f_min - 1.), min(100., f_max + 1.)]
    o2_grid = np.linspace(*display_o2, o2_steps).tolist()
    flow_grid = np.linspace(*display_flow, flow_steps).tolist()

    n_flows = len(flow_grid)
    n_o2s = len(o2_grid)
    total_pts = n_flows * n_o2s
    O2_mesh, F_mesh = np.meshgrid(o2_grid, flow_grid)
    o2_flat = O2_mesh.ravel()
    flow_flat = F_mesh.ravel()

    # Check bounds
    p_min = t_range["pressure_kpa"]["min"]
    p_max = t_range["pressure_kpa"]["max"]
    is_p_valid = (pressure_kpa >= p_min) and (pressure_kpa <= p_max)
    mat_p_min = mat_cfg.get("pressure_kpa", {}).get("min", p_min)
    mat_p_max = mat_cfg.get("pressure_kpa", {}).get("max", p_max)
    is_p_valid = is_p_valid and (pressure_kpa >= mat_p_min) and (pressure_kpa <= mat_p_max)

    valid_mask = (
        is_p_valid
        & (o2_flat >= o2_min)
        & (o2_flat <= o2_max)
        & (flow_flat >= f_min)
        & (flow_flat <= f_max)
    )
    valid_mask = _mask_joint_domain_grid_points(
        o2_flat, flow_flat, material=material, pressure_kpa=pressure_kpa,
        valid_mask=valid_mask,
    )
    valid_mask = _mask_conflicting_grid_points(
        o2_flat, flow_flat, material=material, pressure_kpa=pressure_kpa,
        valid_mask=valid_mask,
    )

    preds_flat: list[str | None] = [None] * total_pts
    probs_flat: list[float | None] = [None] * total_pts

    if valid_mask.any():
        valid_df = pd.DataFrame({
            "oxygen_pct": o2_flat[valid_mask],
            "pressure_kpa": pressure_kpa,
            "flow_cm_s": flow_flat[valid_mask],
            "material": material,
        })
        model_preds = cf_engine.model.predict(valid_df)
        model_probs = cf_engine.model.predict_proba(valid_df)
        spread_idx = (
            list(cf_engine.model.classes_).index("spread")
            if "spread" in cf_engine.model.classes_
            else None
        )

        valid_indices = np.where(valid_mask)[0]
        for i, idx in enumerate(valid_indices):
            preds_flat[idx] = str(model_preds[i])
            if spread_idx is not None:
                probs_flat[idx] = round(float(model_probs[i][spread_idx]), 4)

    grid_predictions = [
        preds_flat[k * n_o2s : (k + 1) * n_o2s] for k in range(n_flows)
    ]
    grid_probabilities = [
        probs_flat[k * n_o2s : (k + 1) * n_o2s] for k in range(n_flows)
    ]

    # Real experiment points for overlay
    df = pd.read_parquet(DATA_PATH)
    mat_df = df[(df["material"] == material) & np.isclose(df["pressure_kpa"], pressure_kpa, rtol=0, atol=0.05)]
    real_pts = []
    for _, r in mat_df.iterrows():
        real_pts.append({
            "experiment_id": r["experiment_id"],
            "report_id": r["report_id"],
            "oxygen_pct": float(r["oxygen_pct"]),
            "flow_cm_s": float(r["flow_cm_s"]),
            "pressure_kpa": float(r["pressure_kpa"]),
            "outcome": r["outcome"],
        })

    return {
        "material": material,
        "fixed_pressure_kpa": pressure_kpa,
        "oxygen_range": display_o2,
        "flow_range": display_flow,
        "oxygen_grid": [round(x, 2) for x in o2_grid],
        "flow_grid": [round(y, 2) for y in flow_grid],
        "grid_predictions": grid_predictions,
        "grid_spread_probabilities": grid_probabilities,
        "real_experiments": real_pts,
        "model": orchestrator.router.get_model_metadata(),
    }


@app.post("/counterfactual", tags=["Counterfactual"])
def run_counterfactual(request: CounterfactualRequest) -> dict[str, Any]:
    """Compute prediction and evidence delta between baseline and modified scenario."""
    _require_model_ready()
    base_dict = request.baseline.model_dump()
    res = cf_engine.compute_perturbation(base_dict, request.changes)
    res["model"] = orchestrator.router.get_model_metadata()
    return res


@app.post("/sweep", tags=["Counterfactual"])
def run_sweep(request: SweepRequest) -> dict[str, Any]:
    """Run a guarded 1-D sweep and identify model regime transitions."""
    _require_model_ready()
    base_dict = request.baseline.model_dump()
    res = cf_engine.run_sweep(
        baseline=base_dict,
        param=request.param,
        start=request.start,
        end=request.end,
        steps=request.steps,
    )
    res["model"] = orchestrator.router.get_model_metadata()
    return res


@app.post("/scenario/parse", tags=["NLP"])
def parse_scenario(request: ParseRequest) -> dict[str, Any]:
    """Parse freeform natural language query into canonical flammability parameters."""
    return interpreter.parse(request.query)


@app.get("/datasets", tags=["Data"])
def list_datasets() -> dict[str, Any]:
    """Return catalog of audited NASA microgravity combustion investigations."""
    if not CATALOG_PATH.exists():
        raise HTTPException(status_code=404, detail="Dataset catalog not found.")

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        items = list(reader)

    return {"count": len(items), "investigations": items}


@app.get("/sources/{report_id:path}", tags=["Data"])
def get_source_document(report_id: str = PathParam(min_length=1, max_length=128)) -> dict[str, Any]:
    """Retrieve metadata, citation, and abstract for a specific NASA report."""
    # Look up by direct ID or normalized string
    doc = corpus_searcher.get_report(report_id)
    if not doc:
        clean_id = report_id.replace("NTRS_", "").replace("NTRS-", "").replace("NTRS ", "")
        doc = corpus_searcher.get_report(clean_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found in corpus.")
    return doc


# ============================================================================
# FLARE-X Evidence Atlas: Conflict Explorer & Comparability Endpoints
# ============================================================================

@app.get("/api/conflict/cases", tags=["Conflict Explorer"])
def list_conflict_cases() -> dict[str, Any]:
    """List canonical NASA research conflict case studies."""
    return {"cases": conflict_engine.list_canonical_cases()}


@app.get("/api/conflict/profiles", tags=["Conflict Explorer"])
def list_conflict_profiles() -> dict[str, Any]:
    """List canonical NASA investigation profiles available for comparability analysis."""
    return {"profiles": conflict_engine.list_study_profiles()}


@app.post("/api/conflict/compare-studies", tags=["Conflict Explorer"])
def compare_studies(request: ConflictStudiesRequest) -> dict[str, Any]:
    """Deep physical comparability analysis between two NASA research investigations."""
    try:
        return conflict_engine.compare_canonical_studies(request.study_a, request.study_b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/conflict/compare-experiments", tags=["Conflict Explorer"])
def compare_experiments(request: ConflictExperimentsRequest) -> dict[str, Any]:
    """Deep comparability and divergence analysis between two specific experiment runs."""
    try:
        return conflict_engine.compare_experiments(request.experiment_id_a, request.experiment_id_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# FLARE-X Evidence Atlas: Research Coverage Map & Knowledge Gaps
# ============================================================================

@app.get("/api/coverage-map", tags=["Coverage Map"])
def get_research_coverage() -> dict[str, Any]:
    """Retrieve indexed dataset coverage and explicitly labeled team proposals."""
    return coverage_engine.get_coverage_summary()


# ============================================================================
# FLARE-X Evidence Atlas: Claim-Level Provenance & Citation Tracing
# ============================================================================

@app.get("/api/provenance/{experiment_id}", tags=["Provenance"])
def get_experiment_provenance(experiment_id: str = PathParam(min_length=1, max_length=128)) -> dict[str, Any]:
    """Retrieve full traceable provenance and original document citation for an experiment."""
    rec = provenance_service.get_provenance(experiment_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found in provenance registry.")
    return rec


@app.get("/api/provenance", tags=["Provenance"])
def query_provenance(
    material: str | None = Query(None, max_length=64, description="Filter by solid material"),
    verification_tier: str | None = Query(None, max_length=128, description="Filter by verification tier"),
    investigation: str | None = Query(None, max_length=128, description="Filter by NASA investigation"),
    search: str | None = Query(None, max_length=256, description="Search keyword in citations/notes"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Query and filter fine-grained provenance records across the NASA corpus."""
    return provenance_service.query_provenance(
        material=material,
        verification_tier=verification_tier,
        investigation=investigation,
        search_query=search,
        limit=limit,
        offset=offset,
    )


from fastapi.staticfiles import StaticFiles

APP_DIR = ROOT / "app"
PROJECT_DIR = ROOT / "project-page"
if PROJECT_DIR.exists():
    app.mount("/project-page", StaticFiles(directory=str(PROJECT_DIR), html=True), name="project-page")
if APP_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(APP_DIR), html=True), name="workbench")
    app.mount("/", StaticFiles(directory=str(APP_DIR), html=True), name="static")
