"""FastAPI Application for FLARE-X Flammability Explorer.

Exposes predictive models, experimental envelope guardrails, nearest-experiment
citations, counterfactual sweeps, and 2-D decision boundary slices.
"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.agents.interpreter import ScenarioInterpreter
from src.agents.orchestrator import AgentOrchestrator
from src.api.schemas import (
    CounterfactualRequest,
    ParseRequest,
    PredictRequest,
    PredictResponse,
    SweepRequest,
)
from src.features.counterfactual import CounterfactualEngine
from src.retrieval.corpus_search import ReportCorpusSearcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flare_x_api")

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cache" / "experiments.parquet"
META_PATH = ROOT / "models" / "model_meta.json"
CORPUS_DIR = ROOT / "cache" / "report_corpus"
CATALOG_PATH = ROOT / "data" / "metadata" / "dataset_catalog.csv"

app = FastAPI(
    title="FLARE-X Microgravity Flammability API",
    description=(
        "Research and operational prototype predicting solid fuel flame-spread regimes "
        "under microgravity conditions using empirical NASA spaceflight data."
    ),
    version="1.0.0",
)

# Enable CORS for local dev and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core engine instances
orchestrator = AgentOrchestrator(meta_path=META_PATH, data_path=DATA_PATH)
cf_engine = CounterfactualEngine(data_path=DATA_PATH, meta_path=META_PATH)
interpreter = ScenarioInterpreter()
corpus_searcher = ReportCorpusSearcher(corpus_dir=CORPUS_DIR)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    """Service health check, dataset status, and model readiness."""
    df = pd.read_parquet(DATA_PATH)
    meta = json.loads(META_PATH.read_bytes())
    return {
        "status": "healthy",
        "service": "FLARE-X Microgravity Flammability Engine",
        "version": "1.0.0",
        "dataset_rows": len(df),
        "dataset_sha256": meta.get("dataset_sha256"),
        "model_type": meta.get("type"),
        "cv_accuracy": meta.get("cv_accuracy"),
        "allowed_materials": meta.get("training_range", {}).get("allowed_materials", []),
    }


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict(request: PredictRequest) -> dict[str, Any]:
    """Predict flammability regime and return nearest experimental citations.

    Conforms strictly to Section 7 API contract.
    If conditions fall outside empirical spaceflight bounds, prediction is refused
    with detailed reasons while still returning the nearest historical experiments.
    """
    payload = request.model_dump()
    res = orchestrator.run(payload)
    return res


@app.get("/experiments", tags=["Data"])
def list_experiments(
    material: str | None = Query(None, description="Filter by solid fuel material"),
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
    meta = json.loads(META_PATH.read_bytes())
    return meta


@app.get("/boundary", tags=["Visualizations"])
def get_decision_boundary(
    material: str = Query("PMMA", description="Material to slice"),
    pressure_kpa: float = Query(101.3, description="Fixed cabin pressure in kPa"),
    o2_steps: int = Query(25, ge=10, le=50, description="Oxygen grid resolution"),
    flow_steps: int = Query(25, ge=10, le=50, description="Flow grid resolution"),
) -> dict[str, Any]:
    """Compute a 2-D decision boundary slice over (oxygen_pct x flow_cm_s).

    Includes real experiments projected onto the 2-D slice for overlay plotting.
    """
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

    # Expand slightly to show boundary edges
    o2_grid = np.linspace(o2_min, o2_max, o2_steps).tolist()
    flow_grid = np.linspace(f_min, f_max, flow_steps).tolist()

    grid_predictions = []
    grid_probabilities = []

    for f_val in flow_grid:
        row_preds = []
        row_probs = []
        for o2_val in o2_grid:
            eval_res = cf_engine.evaluate_scenario(
                oxygen_pct=o2_val,
                pressure_kpa=pressure_kpa,
                flow_cm_s=f_val,
                material=material,
            )
            row_preds.append(eval_res["prediction"])
            row_probs.append(
                eval_res["probabilities"].get("spread")
                if eval_res["probabilities"]
                else None
            )
        grid_predictions.append(row_preds)
        grid_probabilities.append(row_probs)

    # Real experiment points for overlay
    df = pd.read_parquet(DATA_PATH)
    mat_df = df[df["material"] == material]
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
        "oxygen_range": [o2_min, o2_max],
        "flow_range": [f_min, f_max],
        "oxygen_grid": [round(x, 2) for x in o2_grid],
        "flow_grid": [round(y, 2) for y in flow_grid],
        "grid_predictions": grid_predictions,
        "grid_spread_probabilities": grid_probabilities,
        "real_experiments": real_pts,
    }


@app.post("/counterfactual", tags=["Counterfactual"])
def run_counterfactual(request: CounterfactualRequest) -> dict[str, Any]:
    """Compute prediction and evidence delta between baseline and modified scenario."""
    base_dict = request.baseline.model_dump()
    res = cf_engine.compute_perturbation(base_dict, request.changes)
    return res


@app.post("/sweep", tags=["Counterfactual"])
def run_sweep(request: SweepRequest) -> dict[str, Any]:
    """Run 1D parameter sweep to identify flammability regime boundaries and safety margins."""
    base_dict = request.baseline.model_dump()
    res = cf_engine.run_sweep(
        baseline=base_dict,
        param=request.param,
        start=request.start,
        end=request.end,
        steps=request.steps,
    )
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
def get_source_document(report_id: str) -> dict[str, Any]:
    """Retrieve metadata, citation, and abstract for a specific NASA report."""
    # Look up by direct ID or normalized string
    doc = corpus_searcher.get_report(report_id)
    if not doc:
        clean_id = report_id.replace("NTRS_", "").replace("NTRS-", "").replace("NTRS ", "")
        doc = corpus_searcher.get_report(clean_id)
    if not doc:
        # Check by filename stem in CORPUS_DIR
        for p in CORPUS_DIR.glob("*.json"):
            if p.stem == clean_id or p.stem in report_id:
                doc = json.loads(p.read_bytes())
                break
    if not doc:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found in corpus.")
    return doc
