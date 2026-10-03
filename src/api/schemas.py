"""Pydantic schemas for the FLARE-X FastAPI service."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    oxygen_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Oxygen concentration by volume percentage (e.g. 21.0)",
        examples=[21.0],
    )
    pressure_kpa: float = Field(
        ...,
        ge=0.0,
        le=200.0,
        description="Total ambient cabin pressure in kilopascals (e.g. 101.3)",
        examples=[101.3],
    )
    flow_cm_s: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Imposed convective flow velocity in cm/s (e.g. 5.0)",
        examples=[5.0],
    )
    material: str = Field(
        ...,
        description="Solid fuel material name (PMMA, Cotton, Cellulose, Delrin, Nomex)",
        examples=["PMMA"],
    )


class NearestExperimentSchema(BaseModel):
    experiment_id: str | None = None
    report_id: str | None = None
    oxygen_pct: float | None = None
    pressure_kpa: float | None = None
    flow_cm_s: float | None = None
    material: str | None = None
    sample_thickness_mm: float | None = None
    outcome: str | None = None
    distance: float | None = None
    source_url: str | None = None


class ModelMetaSchema(BaseModel):
    type: str
    n_train: int
    cv_accuracy: float
    cv_scheme: str
    features: list[str]


class OutOfRangeReasonSchema(BaseModel):
    feature: str
    value: Any
    train_min: float | None = None
    train_max: float | None = None
    reason: str


class PredictResponse(BaseModel):
    inputs: dict[str, Any]
    in_training_range: bool
    out_of_range_reasons: list[OutOfRangeReasonSchema]
    prediction: str | None = None
    probabilities: dict[str, float] | None = None
    model: ModelMetaSchema
    nearest_experiments: list[dict[str, Any]]
    explanation: str
    status: str | None = None
    sparse_region_warning: bool | None = False
    knn_mean_distance: float | None = None
    warning_message: str | None = None


class CounterfactualRequest(BaseModel):
    baseline: PredictRequest
    changes: dict[str, Any]


class SweepRequest(BaseModel):
    baseline: PredictRequest
    param: Literal["oxygen_pct", "pressure_kpa", "flow_cm_s"]
    start: float
    end: float
    steps: int = Field(default=25, ge=2, le=100)


class ParseRequest(BaseModel):
    query: str
