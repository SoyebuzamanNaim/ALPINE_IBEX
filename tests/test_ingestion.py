"""Automated tests for Phase 04 Data Ingestion."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import pytest

from src.ingestion import build_table

ROOT = Path(__file__).resolve().parents[1]
PARQUET_FILE = ROOT / "cache" / "experiments.parquet"
CSV_FILE = ROOT / "data" / "processed" / "experiments.csv"
MANIFEST_FILE = ROOT / "data" / "metadata" / "source_manifest.csv"
CORPUS_DIR = ROOT / "cache" / "report_corpus"


def _valid_record():
    return {
        "experiment_id": "TEST_001",
        "investigation": "Test Campaign",
        "material": "PMMA",
        "material_raw": "cast PMMA rod",
        "sample_geometry": "rod",
        "sample_thickness_mm": 6.35,
        "oxygen_pct": 20.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "outcome": "spread",
        "outcome_raw": "steady spread",
        "report_id": "20260000001",
        "source_url": "https://ntrs.nasa.gov/citations/20260000001",
    }


def test_ingestion_quarantine_is_persisted_and_stops_dataset_build(tmp_path, monkeypatch):
    invalid = _valid_record()
    invalid["oxygen_pct"] = 120.0
    monkeypatch.setattr(build_table, "load_bass2_relabelled_rows", lambda: [invalid])
    monkeypatch.setattr(build_table, "load_saffire_rows", lambda: [])
    monkeypatch.setattr(build_table, "load_verified_report_rows", lambda: [])
    monkeypatch.setattr(build_table, "INTERIM", tmp_path)
    monkeypatch.setattr(build_table, "INGESTION_AUDIT_PATH", tmp_path / "ingestion_audit.json")
    monkeypatch.setattr(build_table, "QUARANTINE_PATH", tmp_path / "quarantine.json")

    with pytest.raises(build_table.IngestionValidationError, match="1 of 1 source records"):
        build_table.build_full_dataset()

    audit = json.loads((tmp_path / "ingestion_audit.json").read_text())
    assert audit["source_record_count"] == 1
    assert audit["validated_record_count"] == 0
    assert audit["quarantined_record_count"] == 1
    quarantined = json.loads((tmp_path / "quarantine.json").read_text())
    assert quarantined[0]["record"]["experiment_id"] == "TEST_001"
    with pytest.raises(RuntimeError, match="all records were validated"):
        build_table.save_and_report([_valid_record()])


def test_ingestion_audit_reports_zero_quarantine(tmp_path, monkeypatch):
    monkeypatch.setattr(build_table, "load_bass2_relabelled_rows", lambda: [_valid_record()])
    monkeypatch.setattr(build_table, "load_saffire_rows", lambda: [])
    monkeypatch.setattr(build_table, "load_verified_report_rows", lambda: [])
    monkeypatch.setattr(build_table, "INTERIM", tmp_path)
    monkeypatch.setattr(build_table, "INGESTION_AUDIT_PATH", tmp_path / "ingestion_audit.json")
    monkeypatch.setattr(build_table, "QUARANTINE_PATH", tmp_path / "quarantine.json")
    (tmp_path / "quarantine.json").write_text("[]")

    records = build_table.build_full_dataset()
    audit = json.loads((tmp_path / "ingestion_audit.json").read_text())
    assert len(records) == 1
    assert audit["source_record_count"] == 1
    assert audit["validated_record_count"] == 1
    assert audit["quarantined_record_count"] == 0
    assert not (tmp_path / "quarantine.json").exists()

    records[0]["outcome"] = "no_spread"
    with pytest.raises(RuntimeError, match="differ from the latest successful"):
        build_table.save_and_report(records)


def test_files_exist():
    assert PARQUET_FILE.exists(), "cache/experiments.parquet must exist"
    assert CSV_FILE.exists(), "data/processed/experiments.csv must exist"
    assert MANIFEST_FILE.exists(), "source_manifest.csv must exist"
    assert CORPUS_DIR.exists(), "cache/report_corpus must exist"
    assert len(list(CORPUS_DIR.glob("*.json"))) >= 10, "Corpus must contain report JSONs"


def test_row_count_and_reconciliation():
    df_parquet = pd.read_parquet(PARQUET_FILE)
    df_csv = pd.read_csv(CSV_FILE)
    assert len(df_parquet) >= 100, f"Expected at least 100 experiments, got {len(df_parquet)}"
    assert len(df_parquet) == len(df_csv), "Parquet and CSV row counts must match"


def test_no_missing_mandatory_inputs():
    df = pd.read_parquet(PARQUET_FILE)
    mandatory = ["experiment_id", "material", "oxygen_pct", "pressure_kpa", "flow_cm_s", "outcome", "report_id", "source_url"]
    for col in mandatory:
        assert df[col].isnull().sum() == 0, f"Mandatory column {col} has missing values"


def test_no_duplicate_experiment_ids():
    df = pd.read_parquet(PARQUET_FILE)
    duplicates = df[df.duplicated(subset=["experiment_id"])]
    assert len(duplicates) == 0, f"Found duplicate experiment IDs: {duplicates['experiment_id'].tolist()}"


def test_physically_possible_values():
    df = pd.read_parquet(PARQUET_FILE)
    # Oxygen between 10% and 45%
    assert (df["oxygen_pct"] >= 10.0).all() and (df["oxygen_pct"] <= 45.0).all()
    # Pressure between 30 kPa and 150 kPa
    assert (df["pressure_kpa"] >= 30.0).all() and (df["pressure_kpa"] <= 150.0).all()
    # Flow velocity non-negative and under 100 cm/s
    assert (df["flow_cm_s"] >= 0.0).all() and (df["flow_cm_s"] <= 100.0).all()


def test_provenance_and_citations():
    df = pd.read_parquet(PARQUET_FILE)
    # Check URLs start with https://ntrs.nasa.gov/citations/
    assert df["source_url"].str.startswith("https://ntrs.nasa.gov/citations/").all()
    # Check report IDs are non-empty strings
    assert (df["report_id"].str.len() > 4).all()


def test_valid_target_classes():
    df = pd.read_parquet(PARQUET_FILE)
    valid_classes = {"no_spread", "marginal_spread", "spread"}
    actual_classes = set(df["outcome"].unique())
    assert actual_classes.issubset(valid_classes), f"Unexpected classes: {actual_classes - valid_classes}"
    # Verify all 3 classes have representation
    for c in valid_classes:
        assert c in actual_classes, f"Class {c} has 0 representation"


def test_report_corpus_integrity():
    df = pd.read_parquet(PARQUET_FILE)
    report_ids = set(df["report_id"].unique())
    for rid in report_ids:
        corpus_file = CORPUS_DIR / f"{rid}.json"
        assert corpus_file.exists(), f"Missing corpus file for report {rid}"
