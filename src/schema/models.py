"""Pydantic schemas and unit conversion utilities for FLARE-X."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[2]
UNIT_MAP_FILE = ROOT / "data" / "metadata" / "unit_map.json"

MaterialType = Literal["PMMA", "Cotton", "Delrin", "Nomex", "Cellulose"]
GeometryType = Literal["sheet", "rod", "slab", "sphere"]
FlowDirectionType = Literal["opposed", "concurrent", "quiescent"]
RegimeType = Literal["no_spread", "marginal_spread", "spread"]
GravityEnvType = Literal["ISS", "drop_tower", "sounding_rocket", "parabolic"]
ExtractionMethodType = Literal["table_parsed", "digitized_figure", "text_reported"]


class ExperimentRecord(BaseModel):
    """Schema for a single verified microgravity combustion test condition."""
    experiment_id: str = Field(..., description="Unique test run identifier.")
    investigation: str = Field(..., description="NASA investigation family.")
    material: MaterialType = Field(..., description="Standardized material name.")
    material_raw: str = Field(..., description="Verbatim material specification.")
    sample_geometry: GeometryType = Field(..., description="Physical sample geometry.")
    sample_thickness_mm: Optional[float] = Field(None, ge=0.01, le=50.0)
    oxygen_pct: float = Field(..., ge=10.0, le=45.0, description="Ambient O2 percentage by volume.")
    oxygen_raw: Optional[str] = None
    pressure_kpa: float = Field(..., ge=30.0, le=150.0, description="Ambient pressure in kPa.")
    pressure_raw: Optional[str] = None
    flow_cm_s: float = Field(..., ge=0.0, le=100.0, description="Forced flow velocity in cm/s.")
    flow_direction: FlowDirectionType = Field(default="opposed")
    outcome: RegimeType = Field(..., description="Target flame-spread regime.")
    outcome_raw: str = Field(..., description="Verbatim observation.")
    outcome_interpreted: bool = Field(default=False)
    burn_duration_s: Optional[float] = Field(None, ge=0.0)
    spread_rate_mm_s: Optional[float] = Field(None, ge=0.0)
    gravity_env: GravityEnvType = Field(default="ISS")
    report_id: str = Field(..., description="NASA NTRS accession identifier.")
    source_url: str = Field(..., description="Resolvable URL.")
    source_page: Optional[int] = None
    source_table: Optional[str] = None
    extraction_method: ExtractionMethodType = Field(default="table_parsed")
    extraction_notes: Optional[str] = None

    @field_validator("source_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError(f"source_url must be an absolute URL, got: {v}")
        return v


def convert_units(value: float, from_unit: str, dimension: str) -> float:
    """Explicit unit conversion using data/metadata/unit_map.json."""
    if not UNIT_MAP_FILE.exists():
        raise FileNotFoundError(f"Missing unit map file: {UNIT_MAP_FILE}")
    unit_map = json.loads(UNIT_MAP_FILE.read_bytes())
    dim_cfg = unit_map.get("canonical_units", {}).get(dimension)
    if not dim_cfg:
        raise ValueError(f"Unknown dimension: {dimension}")
    conv = dim_cfg.get("conversions", {}).get(from_unit)
    if not conv or not isinstance(conv, dict):
        raise ValueError(f"Cannot convert unit '{from_unit}' for dimension '{dimension}'")
    return value * conv["factor"] + conv.get("offset", 0.0)
