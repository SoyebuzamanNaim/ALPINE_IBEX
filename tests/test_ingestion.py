"""Automated tests for Phase 04 Data Ingestion."""
import hashlib
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PARQUET_FILE = ROOT / "cache" / "experiments.parquet"
CSV_FILE = ROOT / "data" / "processed" / "experiments.csv"
MANIFEST_FILE = ROOT / "data" / "metadata" / "source_manifest.csv"
CORPUS_DIR = ROOT / "cache" / "report_corpus"


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
